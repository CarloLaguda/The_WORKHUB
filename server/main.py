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

    # Delete data from the table before inserting new data
    """
    env_data = pd.read_csv('server/csv_files/env.csv', delimiter=',')

    #Fill the table
    for i,row in env_data.iterrows():
        cursor = mydb.cursor()
        #here %S means string values 
        sql = "INSERT INTO Env VALUES (%s,%s,%s)"
        cursor.execute(sql, tuple(row))
        mydb.commit()# the connection is not auto committed by default, so we must commit to save our changes

    #Check if the table has been filled
    mycursor.execute("SELECT * FROM Env")
    myresult = mycursor.fetchall()
    print("\nEnv\n")
    for x in myresult:
        print(x)
    """
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

    # Delete data from the table before inserting new data
    """
    proj_data = pd.read_csv('server/csv_files/project.csv', delimiter=',')
    
    #Fill the table
    for i,row in proj_data.iterrows():
        cursor = mydb.cursor()
        #here %S means string values 
        sql = "INSERT INTO Project VALUES (%s,%s,%s,%s)"
        cursor.execute(sql, tuple(row))
        mydb.commit()# the connection is not auto committed by default, so we must commit to save our changes

    #Check if the table has been filled
    mycursor.execute("SELECT * FROM Project")
    myresult = mycursor.fetchall()
    print("\nProject\n")
    for x in myresult:
        print(x)
    """
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

    # Delete data from the table before inserting new data
    """
    skill_data = pd.read_csv('server/csv_files/skill.csv', delimiter=',')
    
    #Fill the table
    for i,row in skill_data.iterrows():
        cursor = mydb.cursor()
        #here %S means string values 
        sql = "INSERT INTO Skill VALUES (%s,%s,%s)"
        cursor.execute(sql, tuple(row))
        mydb.commit()# the connection is not auto committed by default, so we must commit to save our changes

    #Check if the table has been filled
    mycursor.execute("SELECT * FROM Skill")
    myresult = mycursor.fetchall()
    print("\nSkill\n")
    for x in myresult:
        print(x)
    """
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

    # Delete data from the table before inserting new data
    """
    user_data = pd.read_csv('server/csv_files/user.csv', delimiter=',')
    
    #Fill the table
    for i,row in user_data.iterrows():
        cursor = mydb.cursor()
        #here %S means string values 
        sql = "INSERT INTO User VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )"
        cursor.execute(sql, tuple(row))
        mydb.commit()# the connection is not auto committed by default, so we must commit to save our changes

    #Check if the table has been filled
    mycursor.execute("SELECT * FROM User")
    myresult = mycursor.fetchall()
    print("\nUser\n")
    for x in myresult:
        print(x)
    """
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

    # Delete data from the table before inserting new data
    """
    user_project_data = pd.read_csv('server/csv_files/project_user.csv', delimiter=',')
    
    #Fill the table
    for i,row in user_project_data.iterrows():
        cursor = mydb.cursor()
        #here %S means string values 
        sql = "INSERT INTO Project_user VALUES (%s,%s,%s,%s)"
        cursor.execute(sql, tuple(row))
        mydb.commit()# the connection is not auto committed by default, so we must commit to save our changes

    #Check if the table has been filled
    mycursor.execute("SELECT * FROM Project_user")
    myresult = mycursor.fetchall()
    print("\nUser_Project\n")
    for x in myresult:
        print(x)
    """
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

    """
    # Delete data from the table before inserting new data
    project_skill_data = pd.read_csv('server/csv_files/skill_project.csv', delimiter=',')
    
    #Fill the table
    for i,row in project_skill_data.iterrows():
        cursor = mydb.cursor()
        #here %S means string values 
        sql = "INSERT INTO Project_user VALUES (%s,%s)"
        cursor.execute(sql, tuple(row))
        mydb.commit()# the connection is not auto committed by default, so we must commit to save our changes

    #Check if the table has been filled
    mycursor.execute("SELECT * FROM Project_skill")
    myresult = mycursor.fetchall()
    print("\nProject_Skill\n")
    for x in myresult:
        print(x)
    """
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


except mysql.connector.Error as err:
    print(f"⚠️ Error connecting to MariaDB: {err}")
finally:
    if 'mydb' in locals() and mydb.is_connected():
        mycursor.close()
        mydb.close()