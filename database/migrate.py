"""
Применяет все миграции из database/migrations/ в порядке нумерации.
Запуск: python -m database.migrate

Таблица __migrations__ хранит уже применённые файлы.
"""
import os
from pathlib import Path
from database.db import get_connection

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def _ensure_migrations_table(conn) -> None:
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS __migrations__ (
            filename VARCHAR(255) PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.close()


def _applied(conn) -> set[str]:
    cur = conn.cursor()
    cur.execute("SELECT filename FROM __migrations__")
    result = {row[0] for row in cur.fetchall()}
    cur.close()
    return result


def run_all() -> None:
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not files:
        print("Нет файлов миграций")
        return

    with get_connection() as conn:
        _ensure_migrations_table(conn)
        done = _applied(conn)

        for f in files:
            if f.name in done:
                print(f"  skip  {f.name}")
                continue

            print(f"  apply {f.name} ...", end=" ")
            sql = f.read_text(encoding="utf-8")
            cur = conn.cursor()
            for stmt in sql.split(";"):
                stmt = stmt.strip()
                if stmt:
                    cur.execute(stmt)
            cur.execute("INSERT INTO __migrations__ (filename) VALUES (%s)", (f.name,))
            cur.close()
            print("ok")

    print("Готово.")


if __name__ == "__main__":
    run_all()
