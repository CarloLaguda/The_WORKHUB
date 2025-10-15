#IMPORTO LIBRERIE NECESSARIE
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import hashlib
from datetime import datetime

app = Flask(__name__)
CORS(app)

mydb = None
mycursor = None

#CONNESIONE A DB
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


#ROTTA PER REGISTRAZIONE UTENTI
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    # --- CAMPI OBBLIGATORI ---
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'eta', 'gender']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    username = data['username']
    email = data['email']

    try:
        # --- Controllo se username esiste già ---
        mycursor.execute("SELECT user_id FROM User WHERE username = %s", (username,))
        existing_user = mycursor.fetchone()
        if existing_user:
            return jsonify({"message": "Username already exists"}), 409  # 409 Conflict

        # (Opzionale) Controllo se email esiste già
        mycursor.execute("SELECT user_id FROM User WHERE email = %s", (email,))
        existing_email = mycursor.fetchone()
        if existing_email:
            return jsonify({"message": "Email already registered"}), 409

        # --- Criptazione password ---
        password_hash = hashlib.sha256(data['password'].encode()).hexdigest()

        # --- Campi opzionali ---
        status = data.get('status') or None
        anni_di_esperienza = data.get('anni_di_esperienza') or None
        country = data.get('country') or None

        # --- Inserimento nuovo utente ---
        mycursor.execute("""
            INSERT INTO User (
                username, email, password, first_name, last_name, eta, gender,
                status, anni_di_esperienza, country
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            username, email, password_hash,
            data['first_name'], data['last_name'],
            data['eta'], data['gender'],
            status, anni_di_esperienza, country
        ))

        mydb.commit()
        return jsonify({"message": "User successfully registered"}), 201

    except mysql.connector.Error as err:
        print(f"Error during registration: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500


#LOGIN UTENTE
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'password' not in data:
        return jsonify({"message": "Password is required"}), 400

    #ACCESSO O CON USERNAME O CON EMAIL
    identifier = data.get('username') or data.get('email')
    if not identifier:
        return jsonify({"message": "Username or email is required"}), 400
    
    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()

    try:
        #CERCO USER O PER USERNAME O PER EMAIL
        mycursor.execute("""
            SELECT user_id, password FROM User WHERE username = %s OR email = %s
        """, (identifier, identifier))
        
        user = mycursor.fetchone()
        #CONFRONTA PASSWORD
        if user and user[1] == password_hash:
            return jsonify({"message": "Login successful", "user_id": user[0]}), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401

    except mysql.connector.Error as err:
        print(f"Database error during login: {err}")
        return jsonify({"error": "Database error"}), 500

#USER
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

    try:
        mycursor.execute(query, tuple(params))
        results = mycursor.fetchall()

        column_names = [desc[0] for desc in mycursor.description]
        response = [dict(zip(column_names, row)) for row in results]

        if user_id and response:
            return jsonify(response[0]), 200
        elif response:
            return jsonify(response), 200
        else:
            return jsonify({"message": "No users found"}), 404

    except mysql.connector.Error as err:
        print(f"Errore durante l'esecuzione della query nella route search_users: {err}")
        return jsonify({"error": "Errore nella query del database"}), 500



#CREAZIONE
@app.route('/api/create_projects', methods=['POST'])
def create_project():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    availability = data.get('availability')  # esempio: 'open' o 'full'
    max_persone = data.get('max_persone')
    creator_user_id = data.get('creator_user_id')

    # Validazione minima (puoi ampliarla)
    if not all([title, description, availability, max_persone, creator_user_id]):
        return jsonify({"message": "Missing required fields"}), 400

    try:
        # Inserisco il progetto
        mycursor.execute("""
            INSERT INTO Project (title, description, availability, max_persone, is_full)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, description, availability, max_persone, 1 if availability == 'full' else 0))

        mydb.commit()

        # Prendo l'id del progetto appena creato
        project_id = mycursor.lastrowid

        # Inserisco la relazione creatore
        mycursor.execute("""
            INSERT INTO Project_user (project_id, user_id, assigned_at, is_creator)
            VALUES (%s, %s, %s, %s)
        """, (project_id, creator_user_id, datetime.now().strftime('%Y-%m-%d'), 1))

        mydb.commit()

        return jsonify({"message": "Project created and creator linked", "project_id": project_id}), 201

    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {err}"}), 400


#LEGARE UN UTENTE AD UN PROGETTO
@app.route('/api/join_user_projects', methods=['POST'])
def join_project():
    data = request.get_json()
    project_id = data['project_id']
    user_id = data['user_id']
    is_creator = data.get('is_creator', 0)  # Default 0 se non specificato
    
    try:
        # Controlla se il progetto è pieno
        mycursor.execute("""
            SELECT is_full FROM Project WHERE project_id = %s
        """, (project_id,))
        project = mycursor.fetchone()
        
        if project and project[0]:
            return jsonify({"message": "Project is full"}), 400
        
        # Inserisco l'utente nel progetto
        mycursor.execute("""
            INSERT INTO Project_user (project_id, user_id, assigned_at, is_creator)
            VALUES (%s, %s, %s, %s)
        """, (project_id, user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), is_creator))
        
        mydb.commit()
        return jsonify({"message": "User successfully joined the project"}), 200
        
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {err}"}), 400
    
#LEGARE SKILL A USER
@app.route('/api/join_projects_skill', methods=['POST'])
def add_skill_to_project():
    data = request.get_json()
    project_id = data['project_id']
    skill_name = data['skill_name']  # Ora ricevi il nome della skill
    
    try:
        # Recupera l'id della skill dal nome
        mycursor.execute("""
            SELECT skill_id FROM Skill WHERE skill_name = %s
        """, (skill_name,))
        result = mycursor.fetchone()
        
        if not result:
            return jsonify({"message": f"Skill '{skill_name}' not found"}), 404
        
        skill_id = result[0]
        
        # Ora inserisci la relazione nel progetto
        mycursor.execute("""
            INSERT INTO Project_skill (project_id, skill_id)
            VALUES (%s, %s)
        """, (project_id, skill_id))

        mydb.commit()
        return jsonify({"message": f"Skill '{skill_name}' successfully added to the project"}), 200
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {err}"}), 400

#LEGARE UN PROGETTO AD UN ENV
@app.route('/api/join_projects_env', methods=['POST'])
def add_env_to_project():
    data = request.get_json()
    project_id = data['project_id']
    env_name = data['env_name']  # Prendiamo il nome dell'env
    
    try:
        # Recupera l'id dell'env dal nome
        mycursor.execute("""
            SELECT ambit_id FROM Env WHERE ambit_name = %s
        """, (env_name,))
        result = mycursor.fetchone()
        
        if not result:
            return jsonify({"message": f"Environment '{env_name}' not found"}), 404
        
        env_id = result[0]
        
        # Inserisci la relazione progetto-env
        mycursor.execute("""
            INSERT INTO Project_env (project_id, ambit_id)
            VALUES (%s, %s)
        """, (project_id, env_id))

        mydb.commit()
        return jsonify({"message": f"Environment '{env_name}' successfully added to the project"}), 200
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {err}"}), 400


#FILTRO PROGETTO PER DETTAGLI
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
            COALESCE(Project_user_count.user_count, 0) AS user_count
        """
    
    base_from_and_joins = """
        FROM Project
        LEFT JOIN Project_skill 
            ON Project.project_id = Project_skill.project_id
        LEFT JOIN Skill 
            ON Project_skill.skill_id = Skill.skill_id
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

    # --- Costruzione dinamica dei filtri ---
    conditions = []
    params = []

    project_id = request.args.get('project_id', type=int)
    disponibilita = request.args.get('availability', type=str)
    skills = request.args.get('skills', type=str)
    creator_name = request.args.get('creator_name', type=str)

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
        # Ricerca su nome e cognome concatenati
        conditions.append("CONCAT(User.first_name, ' ', User.last_name) LIKE %s")
        params.append(f"%{creator_name}%")
    
    # --- Costruzione finale della query ---
    query = base_select + " " + base_from_and_joins

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY Project.project_id ORDER BY Project.project_id"

    # --- Esecuzione query ---
    try:
        if mycursor is None or not mydb.is_connected():
            return jsonify({"error": "Database connection lost or not initialized"}), 503

        mycursor.execute(query, tuple(params))

        if project_id and not disponibilita and not skills and not creator_name:
            project = mycursor.fetchone()
            if not project:
                return jsonify({"message": "Project not found"}), 404

            column_names = [desc[0] for desc in mycursor.description]
            project_dict = dict(zip(column_names, project))
            return jsonify(project_dict), 200

        else:
            projects = mycursor.fetchall()
            if not projects:
                return jsonify({"message": "No projects found matching criteria"}), 404

            column_names = [desc[0] for desc in mycursor.description]
            projects_list = [dict(zip(column_names, p)) for p in projects]
            return jsonify(projects_list), 200

    except mysql.connector.Error as err:
        print(f"Errore durante l'esecuzione della query get_project_details: {err}")
        return jsonify({"error": "Database query error"}), 500

@app.route('/api/user_projects', methods=['GET'])
def get_user_projects():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

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
        LEFT JOIN Project_user creator_link 
            ON p.project_id = creator_link.project_id AND creator_link.is_creator = 1
        LEFT JOIN User u ON creator_link.user_id = u.user_id
        WHERE pu.user_id = %s
        GROUP BY p.project_id, p.title, p.description, p.availability, p.max_persone, p.is_full, creator_name, user_count
        ORDER BY p.project_id;
    """

    try:
        mycursor.execute(query, (user_id,))
        projects = mycursor.fetchall()

        if not projects:
            return jsonify({"message": "No projects found for this user"}), 404

        column_names = [desc[0] for desc in mycursor.description]
        projects_list = [dict(zip(column_names, p)) for p in projects]
        return jsonify(projects_list), 200

    except mysql.connector.Error as err:
        print(f"Database error in get_user_projects: {err}")
        return jsonify({"error": "Database query error"}), 500

@app.route('/api/update_user', methods=['PUT'])
def update_user():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    # 🔧 Tutti i campi aggiornabili nella tabella User, incluso password
    update_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'eta',
        'gender',
        'status',
        'anni_di_esperienza',
        'country',
        'password'  # <--- aggiunto
    ]

    updates = []
    params = []

    for field in update_fields:
        if field in data and data[field] is not None:
            if field == 'password':
                # 🔐 Criptazione della nuova password
                hashed_password = hashlib.sha256(data[field].encode()).hexdigest()
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
        mycursor.execute(query, tuple(params))
        mydb.commit()

        if mycursor.rowcount == 0:
            return jsonify({"message": "User not found"}), 404

        return jsonify({"message": "User information updated successfully"}), 200

    except mysql.connector.Error as err:
        print(f"Error updating user data: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500

@app.route('/api/add_user_skills_by_name', methods=['POST'])
def add_user_skills_by_name():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    user_id = data.get('user_id')
    skill_names = data.get('skill_names')

    if not user_id:
        return jsonify({"message": "User ID is required"}), 400
    if not skill_names or not isinstance(skill_names, list):
        return jsonify({"message": "A list of skill names is required"}), 400

    try:
        # 🔹 Ottieni gli ID delle skill dai nomi
        format_strings = ','.join(['%s'] * len(skill_names))
        mycursor.execute(f"SELECT skill_id, skill_name FROM Skill WHERE skill_name IN ({format_strings})", tuple(skill_names))
        result = mycursor.fetchall()

        if not result:
            return jsonify({"message": "No matching skills found"}), 404

        skill_map = {name: sid for sid, name in result}  # mappa nome -> id
        # Filtra solo le skill esistenti
        existing_skill_ids = list(skill_map.values())

        # 🔹 Recupera le skill già associate all'utente
        mycursor.execute("SELECT skill_id FROM User_skill WHERE user_id = %s", (user_id,))
        already_linked = {row[0] for row in mycursor.fetchall()}

        # 🔹 Filtra solo le nuove skill da inserire
        new_skill_ids = [sid for sid in existing_skill_ids if sid not in already_linked]

        if not new_skill_ids:
            return jsonify({"message": "All provided skills are already linked to the user"}), 200

        # 🔹 Inserimento multiplo
        values = [(user_id, sid) for sid in new_skill_ids]
        mycursor.executemany("INSERT INTO User_skill (user_id, skill_id) VALUES (%s, %s)", values)
        mydb.commit()

        return jsonify({
            "message": "Skills added successfully",
            "added_skills": [name for name in skill_names if name in skill_map and skill_map[name] in new_skill_ids]
        }), 201

    except mysql.connector.Error as err:
        print(f"Database error while adding skills: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500


if __name__ == '__main__':
    # You can change the port as needed
    app.run(debug=True, port=5000)
