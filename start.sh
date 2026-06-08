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

# 4. Заполняем reference_structure из локального манифеста (не нужен MP_API_KEY)
echo "[4/4] Reference structures (local seed)..."
python -m cris.db.schema.seed_local_structures || echo "  WARN: seed_local_structures failed, continuing"

# 5. Опционально: скачиваем новые структуры из Materials Project если есть ключ
if [ -n "${MP_API_KEY}" ]; then
  echo "[5/5] MP download (key found)..."
  for formula in UC2 U2C3 U2N3; do
    python -m cris.tools.dataset_generation.download_structures --formula "$formula" || true
  done
else
  echo "[5/5] MP_API_KEY not set — skipping MP download (local structures only)"
fi

echo "Starting server..."
exec uvicorn backend.api:app --host 0.0.0.0 --port ${PORT:-8002}
