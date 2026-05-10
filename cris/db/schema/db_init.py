"""
Создаёт БД (если нужно) и применяет схему из db_init.sql.

Запуск:
    python -m cris.db.schema.db_init
"""
from pathlib import Path
import psycopg2
from cris.db.config import db_config

sql_file = Path(__file__).parent / "db_init.sql"

# Подключаемся без указания БД, чтобы создать её при необходимости
_admin_cfg = {k: v for k, v in db_config.items() if k != "dbname"}
conn = psycopg2.connect(**_admin_cfg, dbname="postgres")
conn.autocommit = True
cur = conn.cursor()
try:
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_config["dbname"],))
    if not cur.fetchone():
        cur.execute(f'CREATE DATABASE "{db_config["dbname"]}"')
        print(f"База данных '{db_config['dbname']}' создана.")
    else:
        print(f"База данных '{db_config['dbname']}' уже существует.")
finally:
    cur.close()
    conn.close()

# Применяем схему
conn = psycopg2.connect(**db_config)
conn.autocommit = True
cur = conn.cursor()
try:
    cur.execute(sql_file.read_text(encoding="utf-8"))
    print("Схема БД успешно применена.")
except psycopg2.Error as err:
    print(f"Ошибка при создании схемы: {err}")
finally:
    cur.close()
    conn.close()
