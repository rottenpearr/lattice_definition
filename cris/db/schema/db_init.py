"""Инициализирует схему БД из db_init.sql."""
from pathlib import Path
import mysql.connector
from cris.db.config import db_config

sql_file = Path(__file__).parent / "db_init.sql"

conn = mysql.connector.connect(**{k: v for k, v in db_config.items() if k != "database"})
cursor = conn.cursor()
try:
    for stmt in sql_file.read_text(encoding="utf-8").split(";"):
        stmt = stmt.strip()
        if stmt:
            cursor.execute(stmt)
    conn.commit()
    print("Схема БД создана.")
except mysql.connector.Error as err:
    conn.rollback()
    print(f"Ошибка: {err}")
finally:
    cursor.close()
    conn.close()
