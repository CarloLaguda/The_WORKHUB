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


#MEGA SELECT PER USER, POSSIBILE ANCHE FARE SELEZIONI COMBINATE
@app.route('/api/users', methods=['GET'])
def search_users():
    #SELECT DI BASE
    base_select = "SELECT User.user_id, User.username, User.email, User.first_name, User.last_name, User.eta, User.gender, User.status, User.anni_di_esperienza, User.country, GROUP_CONCAT(Skill.skill_name) AS skills"
    base_from_and_joins = """
        FROM User
        LEFT JOIN User_skill ON User.user_id = User_skill.user_id
        LEFT JOIN Skill ON User_skill.skill_id = Skill.skill_id
    """
    
    #CONDIZIONI (WHERE, LIKE) E PARAMETRI
    conditions = []
    params = []

    #PRENDO I PARAMETRI DALLA REQUEST
    user_id = request.args.get('user_id', type=int) #ID
    username_or_email = request.args.get('q', type=str) ##USERNAME O EMAIL
    age = request.args.get('age', type=int) #AGE
    skills = request.args.get('skills', type=str) #SKILLS
    country = request.args.get('country', type=str) #COUNTRY

    #USER ID
    if user_id:
        conditions.append("User.user_id = %s")
        params.append(user_id)
        
    #USERNAME O MAIL
    if username_or_email:
        search_term = '%' + username_or_email + '%'
        conditions.append("(User.username LIKE %s OR User.email LIKE %s)")
        params.extend([search_term, search_term])
        
    #ETà (MAGGIORE O UGUALE)
    if age:
        conditions.append("User.eta >= %s")
        params.append(age)
        
    #PAESE DI NASCITA
    if country:
        conditions.append("User.country = %s")
        params.append(country)

    #NOME SKILL
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

    #COSTRUZIONE QUERY
    query = base_select + base_from_and_joins
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    #GROUP BY
    query += " GROUP BY User.user_id, User.username, User.email, User.first_name, User.last_name, User.eta, User.gender, User.status, User.anni_di_esperienza, User.country"
    #ORDINO IN BASE A USER_ID
    query += " ORDER BY User.user_id"

    #FORMATTO TUTTO IN JSON E INVIA SULLA PAGINA
    try:
        mycursor.execute(query, tuple(params))
        results = mycursor.fetchall()

        # Ottengo i nomi delle colonne per fare il dict
        column_names = [desc[0] for desc in mycursor.description]
        response = [dict(zip(column_names, row)) for row in results]
        
        # 🌟 RESTITUISCO UN SINGOLO OGGETTO SE CERCO PER ID, ALTRIMENTI LA LISTA
        if user_id and response:
            # Se è stato richiesto un singolo ID, restituisci solo il primo elemento (il profilo)
            return jsonify(response[0]), 200
        elif response:
            # Se la ricerca è generica, restituisci la lista
            return jsonify(response), 200
        else:
            return jsonify({"message": "No users found"}), 404

    except mysql.connector.Error as err:
        print(f"Errore durante l'esecuzione della query nella route search_users: {err}")
        return jsonify({"error": "Errore nella query del database"}), 500


#CREAZIONE
@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    
    #INSERT DEI VALORI
    try:
        mycursor.execute("""
            INSERT INTO Project (title, description, availability, max_persone, is_full)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['title'], data['description'], data['availability'], data['max_persone'], data['is_full']))

        mydb.commit()
        return jsonify({"message": "Project successfully created"}), 201
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

#UPDATE USER, PER COUNTRY ANNI EXP E STATUS
@app.route('/api/update_user', methods=['PUT'])
def update_user():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    # 🔧 Tutti i campi aggiornabili nella tabella User
    update_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'eta',
        'gender',
        'status',
        'anni_di_esperienza',
        'country'
    ]

    updates = []
    params = []

    # 🔍 Costruzione dinamica della query (solo i campi presenti nel JSON)
    for field in update_fields:
        if field in data and data[field] is not None:
            updates.append(f"{field} = %s")
            params.append(data[field])

    if not updates:
        return jsonify({"message": "No fields to update"}), 400

    # 🧍‍♂️ Recupera user_id (obbligatorio)
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    # 🧩 Query finale
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
