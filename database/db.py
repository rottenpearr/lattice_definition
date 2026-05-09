import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from contextlib import contextmanager

from database.config import db_config

_pool: MySQLConnectionPool | None = None


def _get_pool() -> MySQLConnectionPool:
    global _pool
    if _pool is None:
        _pool = MySQLConnectionPool(pool_name="crystal_pool", pool_size=5, **db_config)
    return _pool


@contextmanager
def get_connection():
    conn = _get_pool().get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_cursor():
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()


def run_migration(sql_path: str) -> None:
    """Выполнить SQL-файл миграции."""
    with open(sql_path, encoding="utf-8") as f:
        statements = [s.strip() for s in f.read().split(";") if s.strip()]
    with get_connection() as conn:
        cursor = conn.cursor()
        for stmt in statements:
            cursor.execute(stmt)
        cursor.close()
