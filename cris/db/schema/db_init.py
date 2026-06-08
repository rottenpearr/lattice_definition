"""
Создаёт БД (если нужно) и применяет схему из db_init.sql.

Локально: пробует создать БД если не существует.
На Railway/PaaS (DATABASE_URL задан): БД уже создана, сразу применяет схему.

Запуск:
    python -m cris.db.schema.db_init
"""
import os
from pathlib import Path
import psycopg2
from cris.db.config import db_config

sql_file = Path(__file__).parent / "db_init.sql"

# На Railway DATABASE_URL уже указывает на готовую БД — не нужно её создавать
_is_paas = bool(os.getenv("DATABASE_URL", ""))

if not _is_paas:
    # Локально: подключаемся к postgres, создаём БД при необходимости
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
else:
    print("PaaS-режим: база данных уже создана, пропускаем CREATE DATABASE.")

# Применяем схему (CREATE TABLE IF NOT EXISTS — идемпотентно)
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
