"""
Пул соединений и контекстные менеджеры для работы с БД (PostgreSQL / psycopg2).
Использование:
    with get_cursor() as cur:
        cur.execute(...)
        rows = cur.fetchall()
"""
from contextlib import contextmanager
from psycopg2 import pool as pg_pool
from cris.db.config import db_config

_pool: pg_pool.ThreadedConnectionPool | None = None


def _get_pool() -> pg_pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = pg_pool.ThreadedConnectionPool(minconn=1, maxconn=5, **db_config)
    return _pool


@contextmanager
def get_connection():
    conn = _get_pool().getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _get_pool().putconn(conn)


@contextmanager
def get_cursor():
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()
