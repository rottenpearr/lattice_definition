import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
}

sql_file_path = 'init.sql'

with open(sql_file_path, 'r', encoding="UTF-8") as file:
    sql_queries = file.read()

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

try:
    for query in sql_queries.split("\n\n"):
        cursor.execute(query, multi=True)
    print("База данных и таблицы успешно созданы.")
except mysql.connector.Error as err:
    print(f"Ошибка при выполнении SQL: {err}")
finally:
    cursor.close()
    conn.close()
