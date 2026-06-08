#!/bin/bash
set -e

echo "=== CRIS startup ==="

# 1. Создаём схему БД (идемпотентно: CREATE TABLE IF NOT EXISTS)
echo "[1/4] DB schema..."
python -m cris.db.schema.db_init || echo "  WARN: db_init failed, continuing"

# 2. Заполняем справочник типов решёток (ON CONFLICT DO NOTHING)
echo "[2/4] Lattice types..."
python -m cris.db.schema.lattice_types_init || echo "  WARN: lattice_types_init failed, continuing"

# 3. Применяем миграции (CREATE TABLE IF NOT EXISTS — идемпотентно)
echo "[3/4] Migrations..."
python -c "
import psycopg2
from pathlib import Path
from cris.db.config import db_config
migrations = ['cris/db/schema/migrations/001_add_chat_message.sql']
try:
    conn = psycopg2.connect(**db_config)
    conn.autocommit = True
    cur = conn.cursor()
    for f in migrations:
        p = Path(f)
        if p.exists():
            cur.execute(p.read_text(encoding='utf-8'))
            print(f'  Applied: {f}')
    cur.close(); conn.close()
except Exception as e:
    print(f'  WARN: {e}')
"

# 4. Скачиваем эталонные структуры если таблица пустая
echo "[4/4] Reference structures..."
python -c "
import psycopg2, sys, subprocess
from cris.db.config import db_config
try:
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM reference_structure')
    count = cur.fetchone()[0]
    cur.close(); conn.close()
    if count > 0:
        print(f'  Already have {count} structures, skipping download')
        sys.exit(0)
    print('  Table empty, downloading from Materials Project...')
    for formula in ['UC2', 'U2C3', 'U2N3']:
        print(f'  Downloading {formula}...')
        subprocess.run([sys.executable, '-m',
            'cris.tools.dataset_generation.download_structures',
            '--formula', formula], check=False)
except Exception as e:
    print(f'  WARN: {e}')
"

echo "Starting server..."
exec uvicorn backend.api:app --host 0.0.0.0 --port ${PORT:-8002}
