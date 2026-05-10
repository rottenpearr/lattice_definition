"""
Заполняет таблицу lattice_type стандартными типами кристаллических решёток.

Запуск:
    python -m cris.db.schema.lattice_types_init
"""
from pathlib import Path
import psycopg2
from cris.db.config import db_config

sql_file_path = Path(__file__).parent / "lattice_types_init.sql"

conn = psycopg2.connect(**db_config)
cursor = conn.cursor()
try:
    cursor.execute(sql_file_path.read_text(encoding="UTF-8"))
    conn.commit()
    print("В базу данных занесены стандартные типы кристаллических решеток.")
except psycopg2.Error as err:
    conn.rollback()
    print(f"Ошибка при выполнении SQL: {err}")
finally:
    cursor.close()
    conn.close()
