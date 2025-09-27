import mysql.connector
import time

print("Waiting for MariaDB to be ready...")
time.sleep(3)

conn = None # Initialize conn outside the try block
cursor = None # Initialize cursor outside the try block

try:
    conn = mysql.connector.connect(
        host="localhost",
        user = "vscode",
        password="", # empty password
        database="WorkHubDB"
    )
    cursor = conn.cursor()
    
    # 1. Create Table
    cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50));")
    
    # 2. Insert Data
    insert_query = "INSERT INTO test_table (name) VALUES (%s)"
    data_to_insert = ("GianPatrizio",) # Assicurati che sia una tupla (con la virgola)
    
    cursor.execute(insert_query, data_to_insert)
    
    # Commit the changes to the database
    conn.commit()

    print("Database 'WorkHubDB' is ready and table 'test_table' created.")
    print(f"Successfully inserted a record into 'test_table'. Row count: {cursor.rowcount}")

    # ------------------------------------
    # 3. VERIFICA DEI DATI INSERITI (Aggiunto)
    # ------------------------------------
    print("\n--- Verifica dei dati inseriti ---")
    cursor.execute("SELECT id, name FROM test_table;")
    
    # Recupera tutti i risultati
    records = cursor.fetchall()
    
    if records:
        print("Record trovati:")
        for record in records:
            print(f"ID: {record[0]}, Nome: {record[1]}")
    else:
        print("La tabella è vuota, l'inserimento potrebbe non essere riuscito.")
    # ------------------------------------

except mysql.connector.Error as err:
    print(f"Error: {err}")
    
finally:
    if cursor is not None:
        cursor.close()
    if conn is not None and conn.is_connected():
        conn.close()
        print("\nDatabase connection closed.")