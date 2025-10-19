import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv
import logging

# Load environment variables (use path or default to .env in CWD)
load_dotenv("/workspaces/The_WORKHUB/.env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "vscode")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "WorkHubDB")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("init_db")

# Connect to DB (used for initial schema + CSV import)
try:
    mydb = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    mycursor = mydb.cursor()
    log.info("✅ Connessione al database MySQL stabilita con successo!")
except mysql.connector.Error as err:
    mydb = None
    mycursor = None
    log.error(f"⚠️ Errore nella connessione al database: {err}")
    # If we cannot connect, abort the initialization script
    raise SystemExit("Unable to connect to database for initialization.")


try:
    # ----------------------------------------------------------------------------------
    # Tables creation (same as original)
    # ----------------------------------------------------------------------------------

    # Env Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Env (
        ambit_id INT PRIMARY KEY AUTO_INCREMENT,
        ambit_name VARCHAR(100) NOT NULL,
        description VARCHAR(250) NOT NULL
        );
    """)

    # Project Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Project (
        project_id INT PRIMARY KEY AUTO_INCREMENT,
        title VARCHAR(100) NOT NULL,
        description VARCHAR(250) NOT NULL,
        availability VARCHAR(50) NOT NULL,
        max_persone INT NOT NULL,
        is_full BOOLEAN NOT NULL
        );
    """)

    # Skill Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Skill (
        skill_id INT PRIMARY KEY AUTO_INCREMENT,
        skill_name VARCHAR(100) NOT NULL,
        description VARCHAR(255) NOT NULL
        );
    """)

    # User Table
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
        status VARCHAR(50),
        anni_di_esperienza INT,
        country VARCHAR(100)
        );
    """)

    # Project_user Table
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

    # Project_skill Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Project_skill (
        project_id INT NOT NULL,
        skill_id INT NOT NULL,
        PRIMARY KEY (project_id, skill_id),
        FOREIGN KEY (project_id) REFERENCES Project(project_id),
        FOREIGN KEY (skill_id) REFERENCES Skill(skill_id)
    );
    """)

    # Project_env Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Project_env (
        project_id INT NOT NULL,
        ambit_id INT NOT NULL,
        PRIMARY KEY (project_id, ambit_id),
        FOREIGN KEY (project_id) REFERENCES Project(project_id),
        FOREIGN KEY (ambit_id) REFERENCES Env(ambit_id)
    );
    """)

    # User_skill Table
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS User_skill (
        user_id INT NOT NULL,
        skill_id INT NOT NULL,
        PRIMARY KEY (user_id, skill_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (skill_id) REFERENCES Skill(skill_id)
    );
    """)

    mydb.commit()
    log.info("✅ Tables created (or already existed).")

    # ----------------------------------------------------------------------------------
    # CSV import (wrapped with error handling)
    # ----------------------------------------------------------------------------------
    CSV_FILES = [
        'env',
        'user',
        'project',
        'skill',
        'skill_project',
        'project_env',
        'project_user',
        'user_skill'
    ]

    # clear tables in dependency-safe order
    # Use DELETE (as original) but wrap in try/except
    try:
        mycursor.execute("DELETE FROM User_skill")
        mycursor.execute("DELETE FROM Project_env")
        mycursor.execute("DELETE FROM Project_skill")
        mycursor.execute("DELETE FROM Project_user")
        mycursor.execute("DELETE FROM User")
        mycursor.execute("DELETE FROM Skill")
        mycursor.execute("DELETE FROM Project")
        mycursor.execute("DELETE FROM Env")
        mydb.commit()
        log.info("✅ Cleared existing table data.")
    except mysql.connector.Error as err:
        log.warning(f"Non-fatal warning while clearing tables: {err}")
        # continue: maybe tables empty / already cleared

    for files in CSV_FILES:
        try:
            log.info(f"Importing CSV for: {files}")
            match files:
                case 'env':
                    data = pd.read_csv('WorkHub/server/csv_files/env.csv', delimiter=',')
                    for i, row in data.iterrows():
                        cursor = mydb.cursor()
                        sql = "INSERT INTO Env VALUES (%s, %s, %s)"
                        cursor.execute(sql, tuple(row))
                        mydb.commit()

                case 'user':
                    data = pd.read_csv('WorkHub/server/csv_files/user.csv', delimiter=',')
                    for i, row in data.iterrows():
                        cursor = mydb.cursor()
                        sql = "INSERT INTO User VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        cursor.execute(sql, tuple(row))
                        mydb.commit()

                case 'project':
                    data = pd.read_csv('WorkHub/server/csv_files/project.csv', delimiter=',')
                    for i, row in data.iterrows():
                        cursor = mydb.cursor()
                        sql = "INSERT INTO Project VALUES (%s,%s,%s,%s,%s,%s)"
                        cursor.execute(sql, tuple(row))
                        mydb.commit()

                case 'skill':
                    data = pd.read_csv('WorkHub/server/csv_files/skill.csv', delimiter=',')
                    for i, row in data.iterrows():
                        cursor = mydb.cursor()
                        sql = "INSERT INTO Skill VALUES (%s,%s,%s)"
                        cursor.execute(sql, tuple(row))
                        mydb.commit()

                case 'skill_project':
                    data = pd.read_csv('WorkHub/server/csv_files/skill_project.csv', delimiter=',')
                    for i, row in data.iterrows():
                        cursor = mydb.cursor()
                        sql = "INSERT INTO Project_skill VALUES (%s,%s)"
                        cursor.execute(sql, tuple(row))
                        mydb.commit()

                case 'project_env':
                    data = pd.read_csv('WorkHub/server/csv_files/project_env.csv', delimiter=',')
                    for i, row in data.iterrows():
                        cursor = mydb.cursor()
                        sql = "INSERT INTO Project_env VALUES (%s,%s)"
                        cursor.execute(sql, tuple(row))
                        mydb.commit()

                case 'project_user':
                    data = pd.read_csv('WorkHub/server/csv_files/project_user.csv', delimiter=',')
                    for i, row in data.iterrows():
                        cursor = mydb.cursor()
                        sql = "INSERT INTO Project_user VALUES (%s,%s,%s,%s)"
                        cursor.execute(sql, tuple(row))
                        mydb.commit()

                case 'user_skill':
                    data = pd.read_csv('WorkHub/server/csv_files/user_skill.csv', delimiter=',')
                    for i, row in data.iterrows():
                        cursor = mydb.cursor()
                        sql = "INSERT INTO User_skill VALUES (%s,%s)"
                        cursor.execute(sql, tuple(row))
                        mydb.commit()

            log.info(f"✅ Imported CSV for: {files}")
        except FileNotFoundError:
            log.warning(f"CSV for {files} not found — skipping import for that file.")
        except mysql.connector.Error as err:
            log.error(f"Database error while importing {files}: {err}")
        except Exception as ex:
            log.error(f"Unexpected error importing {files}: {ex}")

except mysql.connector.Error as err:
    log.error(f"⚠️ Error connecting to MariaDB during init: {err}")
finally:
    # Close connection used only for initialization
    try:
        if mycursor:
            mycursor.close()
        if mydb and mydb.is_connected():
            mydb.close()
            log.info("🔒 Closed initialization DB connection.")
    except Exception:
        pass