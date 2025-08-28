from pathlib import Path

import mysql.connector

from scripts.config import db_config

sql_file_path = Path("db_init.sql")

with open(sql_file_path, 'r', encoding="UTF-8") as file:
    sql_queries = file.read()

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

try:
    for query in sql_queries.split("\n\n"):
        cursor.execute(query, multi=True)
    conn.commit()
    print("База данных и таблицы успешно созданы.")
except mysql.connector.Error as err:
    conn.rollback()
    print(f"Ошибка при выполнении SQL: {err}")
finally:
    cursor.close()
    conn.close()
