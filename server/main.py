import mysql.connector
import pandas as pd

#Create table
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="vscode",
        password="",
        database="WorkHubDB"
    )
    mycursor = mydb.cursor()
    
    #------------------------------------------------------------------------------------------------------
    #Env Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Env (
        ambit_id INT PRIMARY KEY AUTO_INCREMENT,
        ambit_name VARCHAR(100) NOT NULL,
        description VARCHAR(250) NOT NULL
        );
    """)
    #------------------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------
    #Project Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Project (
        project_id INT PRIMARY KEY AUTO_INCREMENT,
        title VARCHAR(100) NOT NULL,
        description VARCHAR(250) NOT NULL,
        availability VARCHAR(50) NOT NULL
        );
    """)
    #------------------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------
    #Skill Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Skill (
        skill_id INT PRIMARY KEY AUTO_INCREMENT,
        skill_name VARCHAR(100) NOT NULL,
        description VARCHAR(255) NOT NULL
        );
    """)
    #------------------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------
    #User Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        user_id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(255) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL UNIQUE,
        first_name VARCHAR(150) NOT NULL,
        last_name VARCHAR(150) NOT NULL,
        eta INT NOT NULL,   
        password VARCHAR(255) NOT NULL,
        gender CHAR(1) NOT NULL, 
        status VARCHAR(50) NOT NULL,
        anni_di_esperienza INT NOT NULL
        );
    """)
    #------------------------------------------------------------------------------------------------------

    #------------------------------------------------------------------------------------------------------
    #Project_user Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Project_user (
        project_id INT NOT NULL,
        user_id INT NOT NULL,
        assigned_at VARCHAR(50) NOT NULL,
        is_creator BOOLEAN NOT NULL,
        PRIMARY KEY (project_id, user_id, assigned_at),
        FOREIGN KEY (project_id) REFERENCES Project(project_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    );
    """)
    #------------------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------
    #Project_skill Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Project_skill (
        project_id INT NOT NULL,
        skill_id INT NOT NULL,
        PRIMARY KEY (project_id, skill_id),
        FOREIGN KEY (project_id) REFERENCES Project(project_id),
        FOREIGN KEY (skill_id) REFERENCES Skill(skill_id)
    );
    """)
    #------------------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------
    #Project_skill Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Project_env (
        project_id INT NOT NULL,
        ambit_id INT NOT NULL,
        PRIMARY KEY (project_id, ambit_id),
        FOREIGN KEY (project_id) REFERENCES Project(project_id),
        FOREIGN KEY (ambit_id) REFERENCES Env(ambit_id)
    );
    """)
    #------------------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------
    #User_Skill Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS User_skill (
        user_id INT NOT NULL,
        skill_id INT NOT NULL,
        PRIMARY KEY (user_id, skill_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (skill_id) REFERENCES Skill(skill_id)
    );
    """)
    #------------------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------
    CSV_FILES = [
        'env',
        'project',
        'skill',
        'user',

        'skill_project',
        'project_env',
        'project_user',
        'user_skill'
    ]

    mycursor.execute("DELETE FROM User_skill")
    mycursor.execute("DELETE FROM Project_env")
    mycursor.execute("DELETE FROM Project_skill")
    mycursor.execute("DELETE FROM Project_user")
    mycursor.execute("DELETE FROM User")
    mycursor.execute("DELETE FROM Skill")
    mycursor.execute("DELETE FROM Project")
    mycursor.execute("DELETE FROM Env")
    mydb.commit()
    for files in CSV_FILES:
        print(files)
        match files:
            case 'env':
                data = pd.read_csv('server/csv_files/env.csv', delimiter=',')
                for i,row in data.iterrows():
                    cursor = mydb.cursor()
                    sql = "INSERT INTO Env VALUES (%s, %s, %s)"
                    cursor.execute(sql, tuple(row))
                    mydb.commit()

            case 'user':
                data = pd.read_csv('server/csv_files/user.csv', delimiter=',')
                for i,row in data.iterrows():
                    cursor = mydb.cursor()
                    sql = "INSERT INTO User VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, tuple(row))
                    mydb.commit()
            case 'project':
                print("Ciaoo")
                data = pd.read_csv('server/csv_files/project.csv', delimiter=',')
                for i,row in data.iterrows():
                    cursor = mydb.cursor()
                    sql = "INSERT INTO Project VALUES (%s,%s,%s,%s)"
                    cursor.execute(sql, tuple(row))
                    mydb.commit()
            case 'skill':
                data = pd.read_csv('server/csv_files/skill.csv', delimiter=',')
                for i,row in data.iterrows():
                    cursor = mydb.cursor()
                    sql = "INSERT INTO Skill VALUES (%s,%s,%s)"
                    cursor.execute(sql, tuple(row))
                    mydb.commit()
            #Tabelle Relazioni---------------------------------------------------------------------------------------
            case 'skill_project':
                data = pd.read_csv('server/csv_files/skill_project.csv', delimiter=',')
                for i,row in data.iterrows():
                    cursor = mydb.cursor()
                    sql = "INSERT INTO Project_skill VALUES (%s,%s)"
                    cursor.execute(sql, tuple(row))
                    mydb.commit()
                print("Sucaaaaaaaaaaaaa")
            case 'project_env':
                data = pd.read_csv('server/csv_files/project_env.csv', delimiter=',')
                for i,row in data.iterrows():
                    cursor = mydb.cursor()
                    sql = "INSERT INTO Project_env VALUES (%s,%s)"
                    cursor.execute(sql, tuple(row))
                    mydb.commit()
                print("Sucaaaaaaaaaaaaa")
            case 'project_user':
                data = pd.read_csv('server/csv_files/project_user.csv', delimiter=',')
                for i,row in data.iterrows():
                    cursor = mydb.cursor()
                    sql = "INSERT INTO Project_user VALUES (%s,%s,%s,%s)"
                    cursor.execute(sql, tuple(row))
                    mydb.commit()
                print("Sucaaaaaaaaaaaaa")
            case 'user_skill':
                data = pd.read_csv('server/csv_files/user_skill.csv', delimiter=',')
                for i,row in data.iterrows():
                    cursor = mydb.cursor()
                    sql = "INSERT INTO User_skill VALUES (%s,%s)"
                    cursor.execute(sql, tuple(row))
                    mydb.commit()
                print("Sucaaaaaaaaaaaaa")

except mysql.connector.Error as err:
    print(f"⚠️ Error connecting to MariaDB: {err}")
finally:
    if 'mydb' in locals() and mydb.is_connected():
        mycursor.close()
        mydb.close()


"""

            case 'skill_project.csv':
                data = pd.read_csv('server/csv_files/skill_project.csv', delimiter=',')
                for i,row in data.iterrows():
                    cursor = mydb.cursor()
                    sql = "INSERT INTO Project_skill VALUES (%s,%s)"
                    cursor.execute(sql, tuple(row))
            case 'user_skill.csv':
                data = pd.read_csv('server/csv_files/user_skill.csv', delimiter=',')
                for i,row in data.iterrows():
                    cursor = mydb.cursor()
                    sql = "INSERT INTO User_skill (%s,%s)"
                    cursor.execute(sql, tuple(row))
            """