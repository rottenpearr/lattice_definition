import mysql.connector
from config import db_config
from pathlib import Path

sql_file_path = Path("lattice_types_init.sql")

with open(sql_file_path, "r", encoding="UTF-8") as file:
    sql_queries = file.read()

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

try:
    for query in sql_queries.split("\n\n"):
        cursor.execute(query, multi=True)
    conn.commit()
    print("В базу данных занесены стандартные типы кристаллических решеток.")
except mysql.connector.Error as err:
    conn.rollback()
    print(f"Ошибка при выполнении SQL: {err}")
finally:
    cursor.close()
    conn.close()
