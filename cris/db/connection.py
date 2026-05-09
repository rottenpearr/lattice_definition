"""
Пул соединений и контекстные менеджеры для работы с БД.
Использование:
    with get_cursor() as cur:
        cur.execute(...)
        rows = cur.fetchall()
"""
from contextlib import contextmanager
from mysql.connector.pooling import MySQLConnectionPool
from cris.db.config import db_config

_pool: MySQLConnectionPool | None = None


def _get_pool() -> MySQLConnectionPool:
    global _pool
    if _pool is None:
        _pool = MySQLConnectionPool(pool_name="cris_pool", pool_size=5, **db_config)
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
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()
