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
    
    #CAMPI OBBLIGATORI PER LA REGISTRAZIONE
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'eta', 'gender']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    #CRIPTAZIONE PASSWORD
    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()

    # CAMPI DI BASE NULL
    status = data.get('status') or None
    anni_di_esperienza = data.get('anni_di_esperienza') or None
    country = data.get('country') or None

    #INSERT DATI
    try:
        mycursor.execute("""
            INSERT INTO User (
                username, email, password, first_name, last_name, eta, gender,
                status, anni_di_esperienza, country
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['username'], data['email'], password_hash,
            data['first_name'], data['last_name'],
            data['eta'], data['gender'],
            status, anni_di_esperienza, country
        ))
        mydb.commit()
        return jsonify({"message": "User successfully registered"}), 201
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {err}"}), 400


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
        conditions.append("Skill.skill_name = %s")
        params.append(skills)


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


#SELEZIONE PROGETTO
@app.route('/api/all_projects', methods=['GET'])
def get_all_projects():
    try:
        #QUERY PER TUTTI I PROGETTI
        mycursor.execute("SELECT * FROM Project")

        projects = mycursor.fetchall()

        #NOMI COLONNE
        column_names = [desc[0] for desc in mycursor.description]

        #LISTA DIZIONARI
        result = [dict(zip(column_names, project)) for project in projects]

        #MANDA I RISULTATO
        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "No projects found"}), 404

    except mysql.connector.Error as err:
        print(f"Errore durante l'esecuzione della query get_all_projects: {err}")
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
    base_select = "SELECT p.*, GROUP_CONCAT(s.skill_name SEPARATOR ', ') AS required_skills, COALESCE(pu_count.user_count, 0) AS user_count "
    base_from_and_joins = """
        FROM project p
        LEFT JOIN skill_project sp ON p.project_id = sp.project_id
        LEFT JOIN skill s ON sp.skill_id = s.skill_id
        LEFT JOIN (
            SELECT
                project_id,
                COUNT(DISTINCT user_id) AS user_count
            FROM
                project_user
            GROUP BY
                project_id
        ) pu_count ON p.project_id = pu_count.project_id
    """
    
    conditions = []
    params = []

    project_id = request.args.get('project_id', type=int) #ID
    disponibilita = request.args.get('availability', type=str) #DISPONIBILITà
    skills = request.args.get('skills', type=str) #SKILL NAME

    if project_id:
        conditions.append("p.project_id = %s")
        params.append(project_id)
        
    if disponibilita:
        conditions.append("p.availability = %s") 
        params.append(disponibilita)
        
    if skills:
        conditions.append("s.skill_name = %s")
        params.append(skills)
    
    #CONCATENAZIONE QUERY
    query = base_select + base_from_and_joins 
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    group_by_clause = " GROUP BY p.project_id ORDER BY p.project_id" 
    query += group_by_clause

    #SEND JSON
    try:
        if mycursor is None or not mydb.is_connected():
            # Aggiungi un controllo di sicurezza in caso la connessione sia caduta
             return jsonify({"error": "Database connection lost or not initialized"}), 503

        mycursor.execute(query, tuple(params))
        
        # LOGICA DI RITORNO: Singolo oggetto vs. Lista di oggetti
        if project_id and not disponibilita and not skills:
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
        print(f"Errore durante l'esecuzione della query get_project: {err}")
        return jsonify({"error": "Errore nella query del database"}), 500
    
#UNIONE DUTENTE E PROGETTI
@app.route('/api/projects/<int:project_id>/join', methods=['POST'])
def join_project(project_id):
    data = request.get_json()
    user_id = data['user_id']
    
    try:
        #CONTROLLO SE PROGETTO è GIà PEINO
        mycursor.execute("""
            SELECT is_full FROM Project WHERE project_id = %s
        """, (project_id,))
        project = mycursor.fetchone()
        
        if project and project[0]:
            return jsonify({"message": "Project is full"}), 400
        
        mycursor.execute("""
            INSERT INTO Project_user (project_id, user_id, assigned_at, is_creator)
            VALUES (%s, %s, %s, %s)
        """, (project_id, user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0))

        mydb.commit()
        return jsonify({"message": "User successfully joined the project"}), 200
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {err}"}), 400

#UPDATE USER, PER COUNTRY ANNI EXP E STATUS
@app.route('/api/update_user', methods=['PUT'])
def update_user():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    #ALMENO UN DATO DA AGGIORNARE
    update_fields = ['status', 'anni_di_esperienza', 'country']
    updates = []
    params = []

    for field in update_fields:
        if field in data:
            updates.append(f"{field} = %s")
            params.append(data[field])

    if not updates:
        return jsonify({"message": "No fields to update"}), 400

    #AGGIUNGI ID UTENTE
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    #QUERY
    query = f"UPDATE User SET {', '.join(updates)} WHERE user_id = %s"
    params.append(user_id)

    try:
        #ESEGUE QUERY
        mycursor.execute(query, tuple(params))
        mydb.commit()

        if mycursor.rowcount == 0:
            return jsonify({"message": "User not found"}), 404

        return jsonify({"message": "User information updated successfully"}), 200

    except mysql.connector.Error as err:
        print(f"Error updating user data: {err}")
        return jsonify({"message": f"Error: {err}"}), 500


if __name__ == '__main__':
    # You can change the port as needed
    app.run(debug=True, port=5000)
