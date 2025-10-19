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

#CREAZIONE DI UN PROGETTO
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

    cursor = mydb.cursor()

    try:
        # 1. Inserisci il progetto
        cursor.execute("""
            INSERT INTO Project (title, description, availability, max_persone, is_full)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, description, availability, max_persone, 1 if availability == 'full' else 0))
        
        project_id = cursor.lastrowid

        # 2. Inserisci l'associazione col creatore del progetto
        cursor.execute("""
            INSERT INTO Project_user (project_id, user_id, assigned_at, is_creator)
            VALUES (%s, %s, %s, %s)
        """, (project_id, creator_user_id, datetime.now().strftime('%Y-%m-%d'), 1))

        mydb.commit()

        return jsonify({"message": "Project created successfully", "project_id": project_id}), 201

    except mysql.connector.Error as err:
        mydb.rollback()
        return jsonify({"message": f"Error: {err}"}), 400


# LEGARE UN UTENTE AD UN PROGETTO E AGGIORNARE STATUS
@app.route('/api/join_user_projects', methods=['POST'])
def join_project():
    data = request.get_json()
    project_id = data['project_id']
    user_id = data['user_id']
    is_creator = data.get('is_creator', 0)  # Default 0 se non specificato
    
    try:
        # Recupera informazioni sul progetto
        mycursor.execute("""
            SELECT max_persone, is_full FROM Project WHERE project_id = %s
        """, (project_id,))
        project = mycursor.fetchone()
        
        if not project:
            return jsonify({"message": "Project not found"}), 404
        
        max_persone, is_full = project
        
        if is_full:
            return jsonify({"message": "Project is full"}), 400
        
        # Controlla se l'utente è già nel progetto
        mycursor.execute("""
            SELECT 1 FROM Project_user WHERE project_id = %s AND user_id = %s
        """, (project_id, user_id))
        if mycursor.fetchone():
            return jsonify({"message": "User already joined this project"}), 200
        
        # Inserisci l'utente nel progetto
        mycursor.execute("""
            INSERT INTO Project_user (project_id, user_id, assigned_at, is_creator)
            VALUES (%s, %s, %s, %s)
        """, (project_id, user_id, datetime.now().strftime('%Y-%m-%d'), is_creator))
        
        # Conta quanti utenti ci sono ora nel progetto
        mycursor.execute("""
            SELECT COUNT(*) FROM Project_user WHERE project_id = %s
        """, (project_id,))
        current_count = mycursor.fetchone()[0]
        
        # Aggiorna is_full e availability se necessario
        new_is_full = 1 if current_count >= max_persone else 0
        new_availability = 'full' if new_is_full else 'open'
        
        mycursor.execute("""
            UPDATE Project SET is_full = %s, availability = %s WHERE project_id = %s
        """, (new_is_full, new_availability, project_id))
        
        mydb.commit()
        return jsonify({
            "message": "User successfully joined the project",
            "current_users": current_count,
            "is_full": new_is_full,
            "availability": new_availability
        }), 200
        
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {err}"}), 400

    
#LEGARE SKILL A PROJECT
@app.route('/api/join_projects_skill', methods=['POST'])
@app.route('/api/join_projects_skill', methods=['POST'])
def add_skill_to_project():
    data = request.get_json()
    project_id = data.get('project_id')
    skill_name = data.get('skill_name')

    if not all([project_id, skill_name]):
        return jsonify({"message": "Missing required fields"}), 400

    cursor = mydb.cursor()

    try:
        # 1. Recupera l'ID della skill dal nome
        cursor.execute("""
            SELECT skill_id FROM Skill WHERE skill_name = %s
        """, (skill_name,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            return jsonify({"message": f"Skill '{skill_name}' not found"}), 404

        skill_id = result[0]

        # 2. (Facoltativo) Verifica se la skill è già associata
        cursor.execute("""
            SELECT 1 FROM Project_skill WHERE project_id = %s AND skill_id = %s
        """, (project_id, skill_id))
        if cursor.fetchone():
            cursor.close()
            return jsonify({"message": f"Skill '{skill_name}' is already linked to the project"}), 409

        # 3. Inserisci la relazione nel progetto
        cursor.execute("""
            INSERT INTO Project_skill (project_id, skill_id)
            VALUES (%s, %s)
        """, (project_id, skill_id))

        mydb.commit()
        return jsonify({"message": f"Skill '{skill_name}' successfully added to the project"}), 200

    except mysql.connector.Error as err:
        mydb.rollback()
        return jsonify({"message": f"Error: {err}"}), 400


#LEGARE UN PROGETTO AD UN ENV
@app.route('/api/join_projects_env', methods=['POST'])
def add_env_to_project():
    data = request.get_json()
    project_id = data.get('project_id')
    env_name = data.get('env_name')

    if not all([project_id, env_name]):
        return jsonify({"message": "Missing required fields"}), 400

    cursor = mydb.cursor()

    try:
        # 1. Trova l'ambit_id dell'env_name
        cursor.execute("""
            SELECT ambit_id FROM Env WHERE ambit_name = %s
        """, (env_name,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            return jsonify({"message": f"Environment '{env_name}' not found"}), 404

        env_id = result[0]

        # 2. (Facoltativo) Controlla se già esiste
        cursor.execute("""
            SELECT 1 FROM Project_env WHERE project_id = %s AND ambit_id = %s
        """, (project_id, env_id))
        if cursor.fetchone():
            cursor.close()
            return jsonify({"message": f"Environment '{env_name}' is already linked to the project"}), 409

        # 3. Inserisci la relazione
        cursor.execute("""
            INSERT INTO Project_env (project_id, ambit_id)
            VALUES (%s, %s)
        """, (project_id, env_id))

        mydb.commit()
        return jsonify({"message": f"Environment '{env_name}' successfully added to the project"}), 200

    except mysql.connector.Error as err:
        mydb.rollback()
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

    # --- Filtri dinamici ---
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

    # --- Filtro per ambiente corretto ---
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

    # --- Composizione query finale ---
    query = base_select + " " + base_from_and_joins

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY Project.project_id ORDER BY Project.project_id"

    # --- Esecuzione query ---
    try:
        if mycursor is None or not mydb.is_connected():
            return jsonify({"error": "Database connection lost or not initialized"}), 503

        mycursor.execute(query, tuple(params))

        # Caso 1: ricerca per ID singolo
        if project_id and not (disponibilita or skills or creator_name or environment):
            project = mycursor.fetchone()
            if not project:
                return jsonify({"message": "Project not found"}), 404

            column_names = [desc[0] for desc in mycursor.description]
            project_dict = dict(zip(column_names, project))
            return jsonify(project_dict), 200

        # Caso 2: lista di progetti filtrati
        projects = mycursor.fetchall()
        if not projects:
            return jsonify({"message": "No projects found matching criteria"}), 404

        column_names = [desc[0] for desc in mycursor.description]
        projects_list = [dict(zip(column_names, p)) for p in projects]
        return jsonify(projects_list), 200

    except mysql.connector.Error as err:
        print(f"Errore durante l'esecuzione della query get_project_details: {err}")
        return jsonify({"error": "Database query error"}), 500


#PROGETTI DELL'UTENTE LOGGATO
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
        mycursor.execute(query, tuple(params))
        projects = mycursor.fetchall()

        if not projects:
            return jsonify({"message": "No projects found for this user"}), 404

        column_names = [desc[0] for desc in mycursor.description]
        projects_list = [dict(zip(column_names, p)) for p in projects]
        return jsonify(projects_list), 200

    except mysql.connector.Error as err:
        print(f"Database error in get_user_projects: {err}")
        return jsonify({"error": "Database query error"}), 500

#Aggiorna dati utente
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

#Aggiungi una skill allo user
@app.route('/api/add_user_skills_by_name', methods=['POST'])
def add_user_skills_by_name():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    user_id = data.get('user_id')
    skill_name = data.get('skill_names')  # accettiamo solo una stringa ora

    # Validazione parametri
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400
    if not skill_name or not isinstance(skill_name, str):
        return jsonify({"message": "A single skill name as string is required"}), 400

    try:
        mycursor.execute("SELECT skill_id, skill_name FROM Skill WHERE skill_name = %s", (skill_name,))
        result = mycursor.fetchone()

        if not result:
            return jsonify({"message": f"Skill '{skill_name}' not found"}), 404

        skill_id = result[0]

        mycursor.execute("SELECT 1 FROM User_skill WHERE user_id = %s AND skill_id = %s", (user_id, skill_id))
        already_linked = mycursor.fetchone()

        if already_linked:
            return jsonify({"message": f"Skill '{skill_name}' is already linked"}), 200

        mycursor.execute("INSERT INTO User_skill (user_id, skill_id) VALUES (%s, %s)", (user_id, skill_id))
        mydb.commit()

        return jsonify({
            "message": f"Skill '{skill_name}' added successfully"
        }), 201

    except mysql.connector.Error as err:
        print(f"Database error while adding skill: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
