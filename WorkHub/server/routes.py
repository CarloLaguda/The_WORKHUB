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


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    # Campi obbligatori per la registrazione
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'eta', 'gender']

    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    # Hash della password
    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()

    # Campi opzionali — se non presenti diventano automaticamente NULL
    status = data.get('status') or None
    anni_di_esperienza = data.get('anni_di_esperienza') or None
    country = data.get('country') or None

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


# Login utente
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'password' not in data:
        return jsonify({"message": "Password is required"}), 400

    # Prendo l'username o email da 'identifier' (puoi anche usare 'username' o 'email' ma così è più generico)
    identifier = data.get('username') or data.get('email')
    if not identifier:
        return jsonify({"message": "Username or email is required"}), 400

    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()

    try:
        # Query che cerca l'utente sia per username sia per email
        mycursor.execute("""
            SELECT user_id, password FROM User WHERE username = %s OR email = %s
        """, (identifier, identifier))
        
        user = mycursor.fetchone()

        if user and user[1] == password_hash:
            return jsonify({"message": "Login successful", "user_id": user[0]}), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401

    except mysql.connector.Error as err:
        print(f"Database error during login: {err}")
        return jsonify({"error": "Database error"}), 500


# Profilo utente
@app.route('/api/users', methods=['GET'])
def search_users():
    if not mydb or not mycursor:
        return jsonify({"error": "Connessione al database non stabilita"}), 500

    # Colonne da selezionare
    base_select = "SELECT User.user_id, User.username, User.email, User.first_name, User.last_name, User.eta, User.gender, User.status, User.anni_di_esperienza, User.country, GROUP_CONCAT(Skill.skill_name) AS skills"
    
    # Integro in modo INCONDIZIONATO le join per le skill (uso LEFT JOIN, come consigliato, 
    # per non escludere gli utenti senza skill)
    base_from_and_joins = """
        FROM User
        LEFT JOIN User_skill ON User.user_id = User_skill.user_id
        LEFT JOIN Skill ON User_skill.skill_id = Skill.skill_id
    """
    
    conditions = []
    params = []

    # Prendo i parametri dalla query string
    user_id = request.args.get('user_id', type=int)  # 🌟 NUOVO: Ricerca per ID
    username_or_email = request.args.get('q', type=str)
    age = request.args.get('age', type=int)
    skills = request.args.get('skills', type=str)
    country = request.args.get('country', type=str)

    # 🌟 1. Condizione per User ID
    if user_id:
        conditions.append("User.user_id = %s")
        params.append(user_id)
        
    # 2. Ricerca per Username o Email (testo libero)
    if username_or_email:
        search_term = '%' + username_or_email + '%'
        conditions.append("(User.username LIKE %s OR User.email LIKE %s)")
        params.extend([search_term, search_term])
        
    # 3. Condizione per età
    if age:
        conditions.append("User.eta >= %s")
        params.append(age)
        
    # 4. Condizione per Paese
    if country:
        conditions.append("User.country = %s")
        params.append(country)

    # 5. Condizione per Skills
    if skills:
        conditions.append("Skill.skill_name = %s")
        params.append(skills)


    # Costruisco la query completa
    query = base_select + base_from_and_joins
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Aggiungo GROUP BY dato che uso GROUP_CONCAT per le skills
    query += " GROUP BY User.user_id, User.username, User.email, User.first_name, User.last_name, User.eta, User.gender, User.status, User.anni_di_esperienza, User.country"

    # Aggiungo ordinamento per coerenza
    query += " ORDER BY User.user_id"

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

#Selezione progetto
@app.route('/api/all_projects', methods=['GET'])
def get_all_projects():
    try:
        # Esegui la query per ottenere tutti i progetti
        mycursor.execute("SELECT * FROM Project")

        # Recupera i risultati
        projects = mycursor.fetchall()

        # Ottieni i nomi delle colonne
        column_names = [desc[0] for desc in mycursor.description]

        # Crea una lista di dizionari per i risultati
        result = [dict(zip(column_names, project)) for project in projects]

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "No projects found"}), 404

    except mysql.connector.Error as err:
        print(f"Errore durante l'esecuzione della query get_all_projects: {err}")
        return jsonify({"error": "Errore nella query del database"}), 500


# Creazione progetto
@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json()

    try:
        mycursor.execute("""
            INSERT INTO Project (title, description, availability, max_persone, is_full)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['title'], data['description'], data['availability'], data['max_persone'], data['is_full']))

        mydb.commit()
        return jsonify({"message": "Project successfully created"}), 201
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {err}"}), 400

# Dettagli progetto
@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    try:
        mycursor.execute("""
            SELECT * FROM Project WHERE project_id = %s
        """, (project_id,))
        
        project = mycursor.fetchone()
        
        if project:
            # Ottengo i nomi delle colonne dal cursore
            column_names = [desc[0] for desc in mycursor.description]
            # Creo il dict
            project_dict = dict(zip(column_names, project))
            return jsonify(project_dict), 200
        else:
            return jsonify({"message": "Project not found"}), 404

    except mysql.connector.Error as err:
        print(f"Errore durante l'esecuzione della query get_project: {err}")
        return jsonify({"error": "Errore nella query del database"}), 500

       
# Unire un utente a un progetto
@app.route('/api/projects/<int:project_id>/join', methods=['POST'])
def join_project(project_id):
    data = request.get_json()
    user_id = data['user_id']
    
    try:
        # Controlla se il progetto è già pieno
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

# Ricerca progetti
@app.route('/api/projects', methods=['GET'])
def get_projects():
    try:
        # Parametri di filtro (opzionali)
        availability = request.args.get('availability')
        is_full = request.args.get('is_full')
        max_persone = request.args.get('max_persone', type=int)  # esempio di filtro numerico

        # Base query e parametri
        query = "SELECT * FROM Project WHERE 1=1"
        params = []

        # Filtri dinamici
        if availability:
            query += " AND availability = %s"
            params.append(availability)
        if is_full:
            query += " AND is_full = %s"
            params.append(is_full)
        if max_persone is not None:
            query += " AND max_persone <= %s"
            params.append(max_persone)

        # Ordino per project_id
        query += " ORDER BY project_id"

        # Eseguo la query
        mycursor.execute(query, tuple(params))
        projects = mycursor.fetchall()

        # Prendo nomi colonne dinamicamente
        column_names = [desc[0] for desc in mycursor.description]

        # Creo lista di dict
        results = [dict(zip(column_names, project)) for project in projects]

        if results:
            return jsonify(results), 200
        else:
            return jsonify({"message": "No projects found"}), 404

    except mysql.connector.Error as err:
        print(f"Errore durante l'esecuzione della query get_projects: {err}")
        return jsonify({"error": "Errore nella query del database"}), 500


#UPDATE USER
@app.route('/api/update_user', methods=['PUT'])
def update_user():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Missing JSON data"}), 400

    # Verifica che ci sia almeno un dato da aggiornare
    update_fields = ['status', 'anni_di_esperienza', 'country']
    updates = []
    params = []

    for field in update_fields:
        if field in data:
            updates.append(f"{field} = %s")
            params.append(data[field])

    if not updates:
        return jsonify({"message": "No fields to update"}), 400

    # Aggiungi l'ID dell'utente
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    # Prepara la query di aggiornamento
    query = f"UPDATE User SET {', '.join(updates)} WHERE user_id = %s"
    params.append(user_id)

    try:
        # Esegui la query
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
