# ROUTES + API (secure, but same endpoints)
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import hashlib
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd
import bcrypt
import logging

# Rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load env
load_dotenv("/workspaces/The_WORKHUB/.env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "vscode")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "WorkHubDB")

# Logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("routes")

app = Flask(__name__)
CORS(app)

# Configure limiter and attach to app
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])

# DB connection for the API server
try:
    mydb = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    mycursor = mydb.cursor()
    log.info("✅ Connessione al database MySQL stabilita con successo per l'API!")
except mysql.connector.Error as err:
    mydb = None
    mycursor = None
    log.error(f"⚠️ Errore nella connessione al database per l'API: {err}")


# ---------- Helper: safe_query ----------
def safe_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Execute SQL safely and return results.
    - On commit-only insert, returns lastrowid.
    - Returns None on error (and logs the error).
    """
    if not mydb or not mycursor:
        log.error("⚠️ Database connection not available.")
        return None

    try:
        mycursor.execute(query, params or ())
        if commit:
            mydb.commit()
            # if an insert happened, return lastrowid
            try:
                return mycursor.lastrowid
            except Exception:
                return True
        if fetchone:
            return mycursor.fetchone()
        if fetchall:
            return mycursor.fetchall()
        return True
    except mysql.connector.Error as err:
        # Log the full error server-side, but do NOT return details to clients
        log.error(f"MySQL error executing query: {err} -- QUERY: {query} -- PARAMS: {params}")
        return None


# ---------- ROUTES (kept same names & behavior) ----------

# --- REGISTER ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'eta', 'gender']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    username = data['username']
    email = data['email']

    # Check DB connection
    if mycursor is None:
        return jsonify({"message": "Database not initialized"}), 503

    # Use safe_query to check existing username/email
    existing = safe_query("SELECT user_id FROM User WHERE username = %s", (username,), fetchone=True)
    if existing:
        return jsonify({"message": "Username already exists"}), 409

    existing = safe_query("SELECT user_id FROM User WHERE email = %s", (email,), fetchone=True)
    if existing:
        return jsonify({"message": "Email already registered"}), 409

    try:
        # Hash the password with bcrypt
        password_bytes = data['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')

        status = data.get('status') or None
        anni_di_esperienza = data.get('anni_di_esperienza') or None
        country = data.get('country') or None

        insert_query = """
            INSERT INTO User (
                username, email, password, first_name, last_name, eta, gender,
                status, anni_di_esperienza, country
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        res = safe_query(insert_query, (
            username, email, hashed_password,
            data['first_name'], data['last_name'],
            data['eta'], data['gender'],
            status, anni_di_esperienza, country
        ), commit=True)

        if res is None:
            # logged server-side; return generic error to client
            return jsonify({"message": "Internal server error"}), 500

        return jsonify({"message": "User successfully registered"}), 201

    except Exception as e:
        log.error(f"Unexpected error during registration: {e}")
        return jsonify({"message": "Internal server error"}), 500


# --- LOGIN ---
@limiter.limit("5 per minute")
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({"message": "Password is required"}), 400

    # accept either 'username' or 'email' like before
    identifier = data.get('username') or data.get('email')
    if not identifier:
        return jsonify({"message": "Username or email is required"}), 400

    if mycursor is None:
        return jsonify({"error": "Database not initialized"}), 503

    try:
        user = safe_query("""
            SELECT user_id, password FROM User WHERE username = %s OR email = %s
        """, (identifier, identifier), fetchone=True)

        if user:
            # user[1] is stored hashed password (string)
            hashed_password = user[1].encode('utf-8')
            if bcrypt.checkpw(data['password'].encode('utf-8'), hashed_password):
                return jsonify({"message": "Login successful", "user_id": user[0]}), 200

        # unified invalid credentials response (do not reveal whether user exists)
        return jsonify({"message": "Invalid credentials"}), 401

    except Exception as e:
        log.error(f"Database error during login: {e}")
        return jsonify({"error": "Internal server error"}), 500


# --- USERS SEARCH ---
@app.route('/api/users', methods=['GET'])
def search_users():
    base_select = """
        SELECT 
            User.user_id,
            User.username,
            User.email,
            User.first_name,
            User.last_name,
            User.eta,
            User.gender,
            User.status,
            User.anni_di_esperienza,
            User.country,
            User.password,
            GROUP_CONCAT(Skill.skill_name) AS skills
    """

    base_from_and_joins = """
        FROM User
        LEFT JOIN User_skill ON User.user_id = User_skill.user_id
        LEFT JOIN Skill ON User_skill.skill_id = Skill.skill_id
    """

    conditions = []
    params = []

    user_id = request.args.get('user_id', type=int)
    username_or_email = request.args.get('q', type=str)
    age = request.args.get('age', type=int)
    skills = request.args.get('skills', type=str)
    country = request.args.get('country', type=str)

    if user_id:
        conditions.append("User.user_id = %s")
        params.append(user_id)

    if username_or_email:
        search_term = '%' + username_or_email + '%'
        conditions.append("(User.username LIKE %s OR User.email LIKE %s)")
        params.extend([search_term, search_term])

    if age:
        conditions.append("User.eta >= %s")
        params.append(age)

    if country:
        conditions.append("User.country = %s")
        params.append(country)

    if skills:
        conditions.append("""
            User.user_id IN (
                SELECT us.user_id 
                FROM User_skill us
                JOIN Skill s ON us.skill_id = s.skill_id
                WHERE s.skill_name LIKE %s
            )
        """)
        params.append(f"%{skills}%")

    query = base_select + " " + base_from_and_joins
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        GROUP BY 
            User.user_id, 
            User.username, 
            User.email, 
            User.first_name, 
            User.last_name, 
            User.eta, 
            User.gender, 
            User.status, 
            User.anni_di_esperienza, 
            User.country,
            User.password
        ORDER BY User.user_id
    """

    if mycursor is None:
        return jsonify({"error": "Database not initialized"}), 503

    try:
        rows = safe_query(query, tuple(params), fetchall=True)
        if rows is None:
            return jsonify({"error": "Internal server error"}), 500

        # Reuse existing description to get column names (same as original behavior)
        column_names = [desc[0] for desc in mycursor.description] if mycursor.description else []
        response = [dict(zip(column_names, row)) for row in rows]

        if user_id and response:
            return jsonify(response[0]), 200
        elif response:
            return jsonify(response), 200
        else:
            return jsonify({"message": "No users found"}), 404

    except Exception as e:
        log.error(f"Errore durante l'esecuzione della query nella route search_users: {e}")
        return jsonify({"error": "Errore nella query del database"}), 500


# --- CREATE PROJECT ---
@app.route('/api/create_projects', methods=['POST'])
def create_project():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    availability = data.get('availability', 'open')
    max_persone = data.get('max_persone')
    creator_user_id = data.get('creator_user_id')

    if not all([title, description, max_persone, creator_user_id]):
        return jsonify({"message": "Missing required fields"}), 400

    if mycursor is None:
        return jsonify({"error": "Database not initialized"}), 503

    try:
        insert_project_q = """
            INSERT INTO Project (title, description, availability, max_persone, is_full)
            VALUES (%s, %s, %s, %s, %s)
        """
        project_id = safe_query(insert_project_q, (title, description, availability, max_persone, 1 if availability == 'full' else 0), commit=True)
        if project_id is None:
            return jsonify({"message": "Internal server error"}), 500

        # Insert project_user
        insert_pu_q = """
            INSERT INTO Project_user (project_id, user_id, assigned_at, is_creator)
            VALUES (%s, %s, %s, %s)
        """
        res = safe_query(insert_pu_q, (project_id, creator_user_id, datetime.now().strftime('%Y-%m-%d'), 1), commit=True)
        if res is None:
            return jsonify({"message": "Internal server error"}), 500

        return jsonify({"message": "Project created successfully", "project_id": project_id}), 201

    except Exception as e:
        log.error(f"Error in create_project: {e}")
        return jsonify({"message": "Internal server error"}), 500


# --- JOIN USER TO PROJECT ---
@app.route('/api/join_user_projects', methods=['POST'])
def join_project():
    data = request.get_json()
    project_id = data['project_id']
    user_id = data['user_id']
    is_creator = data.get('is_creator', 0)

    if mycursor is None:
        return jsonify({"error": "Database not initialized"}), 503

    try:
        project = safe_query("SELECT max_persone, is_full FROM Project WHERE project_id = %s", (project_id,), fetchone=True)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        max_persone, is_full = project

        if is_full:
            return jsonify({"message": "Project is full"}), 400

        already = safe_query("SELECT 1 FROM Project_user WHERE project_id = %s AND user_id = %s", (project_id, user_id), fetchone=True)
        if already:
            return jsonify({"message": "User already joined this project"}), 200

        res = safe_query("INSERT INTO Project_user (project_id, user_id, assigned_at, is_creator) VALUES (%s, %s, %s, %s)",
                         (project_id, user_id, datetime.now().strftime('%Y-%m-%d'), is_creator), commit=True)
        if res is None:
            return jsonify({"message": "Internal server error"}), 500

        current_count = safe_query("SELECT COUNT(*) FROM Project_user WHERE project_id = %s", (project_id,), fetchone=True)
        if current_count is None:
            return jsonify({"message": "Internal server error"}), 500
        # current_count is a tuple like (N,)
        count_val = current_count[0] if isinstance(current_count, (list, tuple)) else int(current_count)

        new_is_full = 1 if count_val >= max_persone else 0
        new_availability = 'full' if new_is_full else 'open'

        update_res = safe_query("UPDATE Project SET is_full = %s, availability = %s WHERE project_id = %s",
                                (new_is_full, new_availability, project_id), commit=True)
        if update_res is None:
            return jsonify({"message": "Internal server error"}), 500

        return jsonify({
            "message": "User successfully joined the project",
            "current_users": count_val,
            "is_full": new_is_full,
            "availability": new_availability
        }), 200

    except Exception as e:
        log.error(f"Error in join_project: {e}")
        return jsonify({"message": "Internal server error"}), 500


# --- ADD SKILL TO PROJECT ---
@app.route('/api/join_projects_skill', methods=['POST'])
def add_skill_to_project():
    data = request.get_json()
    project_id = data['project_id']
    skill_name = data['skill_name']

    if mycursor is None:
        return jsonify({"error": "Database not initialized"}), 503

    try:
        result = safe_query("SELECT skill_id FROM Skill WHERE skill_name = %s", (skill_name,), fetchone=True)
        if not result:
            return jsonify({"message": f"Skill '{skill_name}' not found"}), 404

        skill_id = result[0]
        res = safe_query("INSERT INTO Project_skill (project_id, skill_id) VALUES (%s, %s)", (project_id, skill_id), commit=True)
        if res is None:
            return jsonify({"message": "Internal server error"}), 500

        return jsonify({"message": f"Skill '{skill_name}' successfully added to the project"}), 200

    except Exception as e:
        log.error(f"Error in add_skill_to_project: {e}")
        return jsonify({"message": "Internal server error"}), 500


# --- ADD ENV TO PROJECT ---
@app.route('/api/join_projects_env', methods=['POST'])
def add_env_to_project():
    data = request.get_json()
    project_id = data['project_id']
    env_name = data['env_name']

    if mycursor is None:
        return jsonify({"error": "Database not initialized"}), 503

    try:
        result = safe_query("SELECT ambit_id FROM Env WHERE ambit_name = %s", (env_name,), fetchone=True)
        if not result:
            return jsonify({"message": f"Environment '{env_name}' not found"}), 404

        env_id = result[0]
        res = safe_query("INSERT INTO Project_env (project_id, ambit_id) VALUES (%s, %s)", (project_id, env_id), commit=True)
        if res is None:
            return jsonify({"message": "Internal server error"}), 500

        return jsonify({"message": f"Environment '{env_name}' successfully added to the project"}), 200

    except Exception as e:
        log.error(f"Error in add_env_to_project: {e}")
        return jsonify({"message": "Internal server error"}), 500


# --- PROJECT DETAILS FILTER ---
@app.route('/api/projects_details', methods=['GET'])
def get_project_details():
    base_select = """
    SELECT
        Project.project_id,
        Project.title,
        Project.description,
        Project.availability,
        Project.max_persone,
        Project.is_full,
        CONCAT(User.first_name, ' ', User.last_name) AS creator_name,
        GROUP_CONCAT(DISTINCT Skill.skill_name SEPARATOR ', ') AS required_skills,
        GROUP_CONCAT(DISTINCT Env.ambit_name SEPARATOR ', ') AS environments,
        COALESCE(Project_user_count.user_count, 0) AS user_count
    """

    base_from_and_joins = """
        FROM Project
        LEFT JOIN Project_skill 
            ON Project.project_id = Project_skill.project_id
        LEFT JOIN Skill 
            ON Project_skill.skill_id = Skill.skill_id
        LEFT JOIN Project_env 
            ON Project.project_id = Project_env.project_id
        LEFT JOIN Env 
            ON Project_env.ambit_id = Env.ambit_id
        LEFT JOIN (
            SELECT 
                project_id,
                COUNT(DISTINCT user_id) AS user_count
            FROM Project_user
            GROUP BY project_id
        ) AS Project_user_count 
            ON Project.project_id = Project_user_count.project_id
        LEFT JOIN Project_user AS Creator_link 
            ON Project.project_id = Creator_link.project_id AND Creator_link.is_creator = 1
        LEFT JOIN User 
            ON Creator_link.user_id = User.user_id
    """

    conditions = []
    params = []

    project_id = request.args.get('project_id', type=int)
    disponibilita = request.args.get('availability', type=str)
    skills = request.args.get('skills', type=str)
    creator_name = request.args.get('creator_name', type=str)
    environment = request.args.get('environment', type=str)

    if project_id:
        conditions.append("Project.project_id = %s")
        params.append(project_id)

    if disponibilita:
        conditions.append("Project.availability = %s")
        params.append(disponibilita)

    if skills:
        conditions.append("Skill.skill_name LIKE %s")
        params.append(f"%{skills}%")

    if creator_name:
        conditions.append("CONCAT(User.first_name, ' ', User.last_name) LIKE %s")
        params.append(f"%{creator_name}%")

    if environment:
        conditions.append("""
            Project.project_id IN (
                SELECT Project_env.project_id
                FROM Project_env
                JOIN Env ON Project_env.ambit_id = Env.ambit_id
                WHERE Env.ambit_name LIKE %s
            )
        """)
        params.append(f"%{environment}%")

    query = base_select + " " + base_from_and_joins
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY Project.project_id ORDER BY Project.project_id"

    if mycursor is None:
        return jsonify({"error": "Database not initialized"}), 503

    try:
        rows = safe_query(query, tuple(params), fetchall=True)
        if rows is None:
            return jsonify({"error": "Database query error"}), 500

        # If searching by single ID without other filters, return single project
        if project_id and not (disponibilita or skills or creator_name or environment):
            project = rows[0] if rows else None
            if not project:
                return jsonify({"message": "Project not found"}), 404

            column_names = [desc[0] for desc in mycursor.description] if mycursor.description else []
            project_dict = dict(zip(column_names, project))
            return jsonify(project_dict), 200

        if not rows:
            return jsonify({"message": "No projects found matching criteria"}), 404

        column_names = [desc[0] for desc in mycursor.description] if mycursor.description else []
        projects_list = [dict(zip(column_names, p)) for p in rows]
        return jsonify(projects_list), 200

    except Exception as e:
        log.error(f"Errore durante l'esecuzione della query get_project_details: {e}")
        return jsonify({"error": "Database query error"}), 500


# --- USER PROJECTS ---
@app.route('/api/user_projects', methods=['GET'])
def get_user_projects():
    user_id = request.args.get('user_id', type=int)

    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    if mycursor is None:
        return jsonify({"error": "Database not initialized"}), 503

    query = """
        SELECT 
            p.project_id,
            p.title,
            p.description,
            p.availability,
            p.max_persone,
            p.is_full,
            CONCAT(u.first_name, ' ', u.last_name) AS creator_name,
            GROUP_CONCAT(DISTINCT s.skill_name SEPARATOR ', ') AS required_skills,
            GROUP_CONCAT(DISTINCT e.ambit_name SEPARATOR ', ') AS environments,
            COALESCE(pc.user_count, 0) AS user_count
        FROM Project p
        JOIN Project_user pu ON p.project_id = pu.project_id
        LEFT JOIN (
            SELECT project_id, COUNT(DISTINCT user_id) AS user_count
            FROM Project_user
            GROUP BY project_id
        ) AS pc ON p.project_id = pc.project_id
        LEFT JOIN Project_skill ps ON p.project_id = ps.project_id
        LEFT JOIN Skill s ON ps.skill_id = s.skill_id
        LEFT JOIN Project_env pe ON p.project_id = pe.project_id
        LEFT JOIN Env e ON pe.ambit_id = e.ambit_id
        LEFT JOIN Project_user creator_link 
            ON p.project_id = creator_link.project_id AND creator_link.is_creator = 1
        LEFT JOIN User u ON creator_link.user_id = u.user_id
        WHERE pu.user_id = %s
    """

    params = [user_id]

    query += """
        GROUP BY 
            p.project_id, 
            p.title, 
            p.description, 
            p.availability, 
            p.max_persone, 
            p.is_full, 
            creator_name, 
            user_count
        ORDER BY p.project_id;
    """

    try:
        rows = safe_query(query, tuple(params), fetchall=True)
        if rows is None:
            return jsonify({"error": "Database query error"}), 500

        if not rows:
            return jsonify({"message": "No projects found for this user"}), 404

        column_names = [desc[0] for desc in mycursor.description] if mycursor.description else []
        projects_list = [dict(zip(column_names, p)) for p in rows]
        return jsonify(projects_list), 200

    except Exception as e:
        log.error(f"Database error in get_user_projects: {e}")
        return jsonify({"error": "Database query error"}), 500


# --- UPDATE USER ---
@app.route('/api/update_user', methods=['PUT'])
def update_user():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    update_fields = [
        'username',
        'email',
        'status',
        'anni_di_esperienza',
        'country',
        'password'
    ]

    updates = []
    params = []

    for field in update_fields:
        if field in data and data[field] is not None:
            if field == 'password':
                hashed_password = bcrypt.hashpw(data[field].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                updates.append(f"{field} = %s")
                params.append(hashed_password)
            else:
                updates.append(f"{field} = %s")
                params.append(data[field])

    if not updates:
        return jsonify({"message": "No fields to update"}), 400

    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    query = f"UPDATE User SET {', '.join(updates)} WHERE user_id = %s"
    params.append(user_id)

    try:
        res = safe_query(query, tuple(params), commit=True)
        if res is None:
            return jsonify({"message": "Database error"}), 500

        if mycursor.rowcount == 0:
            return jsonify({"message": "User not found"}), 404

        return jsonify({"message": "User information updated successfully"}), 200

    except Exception as e:
        log.error(f"Error updating user data: {e}")
        return jsonify({"message": "Internal server error"}), 500


# --- ADD USER SKILL BY NAME ---
@app.route('/api/add_user_skills_by_name', methods=['POST'])
def add_user_skills_by_name():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    user_id = data.get('user_id')
    skill_name = data.get('skill_names')  # as original

    if not user_id:
        return jsonify({"message": "User ID is required"}), 400
    if not skill_name or not isinstance(skill_name, str):
        return jsonify({"message": "A single skill name as string is required"}), 400

    try:
        result = safe_query("SELECT skill_id, skill_name FROM Skill WHERE skill_name = %s", (skill_name,), fetchone=True)
        if not result:
            return jsonify({"message": f"Skill '{skill_name}' not found"}), 404

        skill_id = result[0]
        already_linked = safe_query("SELECT 1 FROM User_skill WHERE user_id = %s AND skill_id = %s", (user_id, skill_id), fetchone=True)
        if already_linked:
            return jsonify({"message": f"Skill '{skill_name}' is already linked to user"}), 200

        res = safe_query("INSERT INTO User_skill (user_id, skill_id) VALUES (%s, %s)", (user_id, skill_id), commit=True)
        if res is None:
            return jsonify({"message": "Database error"}), 500

        return jsonify({"message": f"Skill '{skill_name}' added successfully to user {user_id}"}), 201

    except Exception as e:
        log.error(f"Database error while adding skill: {e}")
        return jsonify({"message": "Internal server error"}), 500


# ---------- Global error handlers ----------
@app.errorhandler(500)
def internal_error(error):
    log.error(f"Internal Server Error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


# ---------- Run app ----------
if __name__ == '__main__':
    # Keep debug controlled by env var (do not leave debug True in production)
    debug_flag = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_flag, port=int(os.getenv("PORT", 5000)))