from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

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
        mycursor.execute('''SELECT User.first_name, User.last_name, User.eta, User.gender, 
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

if __name__ == '__main__':
    # You can change the port as needed
    app.run(debug=True, port=5000)
