from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import hashlib
from datetime import datetime

app = Flask(__name__)
CORS(app)

mydb = None
mycursor = None

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="vscode",
        password="",
        database="WorkHubDB"
    )
    mycursor = mydb.cursor()
    print("Connessione al database MySQL stabilita con successo!")
except mysql.connector.Error as err:
    print(f"⚠️ Error connecting to MariaDB: {err}")


@app.route("/")
def main():
    return f"Ciao Amici io mi chiamo GIGI"

@app.route("/workers_general")
def workers():
    if not mydb or not mycursor:
        return jsonify({"error": "Connessione al database non stabilita"}), 500
    try:
        mycursor.execute('''SELECT User.first_name, User.last_name, User.eta, User.gender, User.country,
                            User.status, User.anni_di_esperienza, GROUP_CONCAT(Skill.skill_name SEPARATOR ', ') AS skill_names_list
                            FROM User
                            INNER JOIN User_skill ON User.user_id = User_skill.user_id
                            INNER JOIN Skill ON User_skill.skill_id = Skill.skill_id
                            GROUP BY User.user_id, User.first_name, User.last_name, User.eta, User.gender, User.status, User.anni_di_esperienza
                            ORDER BY User.user_id;
                            ''' )
        myresult = mycursor.fetchall()
        column_names = [desc[0] for desc in mycursor.description]
        result = []
        for row in myresult:
            row_dict = dict(zip(column_names, row))
            result.append(row_dict)
        return jsonify(result)
    except mysql.connector.Error as err:
        print(f"Errore durante l'esecuzione della query nella route MostPole: {err}")
        return jsonify({"error": "Errore nella query del database"}), 500

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO User (username, email, password, first_name, last_name, eta, gender, status, anni_di_esperienza, country)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['username'], data['email'], password_hash, data['first_name'], data['last_name'],
              data['eta'], data['gender'], data['status'], data['anni_di_esperienza'], data['country']))

        conn.commit()
        return jsonify({"message": "User successfully registered"}), 201
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {err}"}), 400
    finally:
        cursor.close()
        conn.close()

# Login utente
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, password FROM User WHERE email = %s
    """, (data['email'],))
    
    user = cursor.fetchone()
    
    if user and user[1] == password_hash:
        return jsonify({"message": "Login successful", "user_id": user[0]}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
    finally:
        cursor.close()
        conn.close()

# Profilo utente
@app.route('/api/profile', methods=['GET'])
def get_profile():
    user_id = request.args.get('user_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, username, email, first_name, last_name, eta, gender, status, anni_di_esperienza, country
        FROM User WHERE user_id = %s
    """, (user_id,))
    
    user = cursor.fetchone()
    
    if user:
        return jsonify(dict(zip(['user_id', 'username', 'email', 'first_name', 'last_name', 'eta', 'gender', 'status', 'anni_di_esperienza', 'country'], user))), 200
    else:
        return jsonify({"message": "User not found"}), 404
    finally:
        cursor.close()
        conn.close()

# Ricerca utenti
@app.route('/api/users', methods=['GET'])
def search_users():
    age = request.args.get('age')
    skills = request.args.get('skills')
    country = request.args.get('country')

    query = "SELECT * FROM User WHERE 1=1"
    params = []
    
    if age:
        query += " AND eta = %s"
        params.append(age)
    if skills:
        query += " AND user_id IN (SELECT user_id FROM User_skill WHERE skill_id IN (%s))"
        params.append(skills)
    if country:
        query += " AND country = %s"
        params.append(country)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(query, tuple(params))
    users = cursor.fetchall()

    if users:
        return jsonify([dict(zip(['user_id', 'username', 'email', 'first_name', 'last_name', 'eta', 'gender', 'status', 'anni_di_esperienza', 'country'], user)) for user in users]), 200
    else:
        return jsonify({"message": "No users found"}), 404
    finally:
        cursor.close()
        conn.close()

# Creazione progetto
@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Project (title, description, availability, max_persone, is_full)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['title'], data['description'], data['availability'], data['max_persone'], data['is_full']))

        conn.commit()
        return jsonify({"message": "Project successfully created"}), 201
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {err}"}), 400
    finally:
        cursor.close()
        conn.close()

# Dettagli progetto
@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM Project WHERE project_id = %s
    """, (project_id,))
    
    project = cursor.fetchone()
    
    if project:
        return jsonify(dict(zip(['project_id', 'title', 'description', 'availability', 'max_persone', 'is_full'], project))), 200
    else:
        return jsonify({"message": "Project not found"}), 404
    finally:
        cursor.close()
        conn.close()

# Unire un utente a un progetto
@app.route('/api/projects/<int:project_id>/join', methods=['POST'])
def join_project(project_id):
    data = request.get_json()
    user_id = data['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Controlla se il progetto è già pieno
        cursor.execute("""
            SELECT is_full FROM Project WHERE project_id = %s
        """, (project_id,))
        project = cursor.fetchone()
        
        if project and project[0]:
            return jsonify({"message": "Project is full"}), 400
        
        cursor.execute("""
            INSERT INTO Project_user (project_id, user_id, assigned_at, is_creator)
            VALUES (%s, %s, %s, %s)
        """, (project_id, user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0))

        conn.commit()
        return jsonify({"message": "User successfully joined the project"}), 200
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {err}"}), 400
    finally:
        cursor.close()
        conn.close()

# Ricerca progetti
@app.route('/api/projects', methods=['GET'])
def get_projects():
    availability = request.args.get('availability')
    is_full = request.args.get('is_full')

    query = "SELECT * FROM Project WHERE 1=1"
    params = []
    
    if availability:
        query += " AND availability = %s"
        params.append(availability)
    if is_full:
        query += " AND is_full = %s"
        params.append(is_full)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(query, tuple(params))
    projects = cursor.fetchall()

    if projects:
        return jsonify([dict(zip(['project_id', 'title', 'description', 'availability', 'max_persone', 'is_full'], project)) for project in projects]), 200
    else:
        return jsonify({"message": "No projects found"}), 404
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    # You can change the port as needed
    app.run(debug=True, port=5000)
