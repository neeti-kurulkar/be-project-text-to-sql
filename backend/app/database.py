import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from app.config import settings

# Connection pool
connection_pool = None


def init_db_pool():
    """Initialize database connection pool"""
    global connection_pool
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20,
        host=settings.PGHOST,
        port=settings.PGPORT,
        database=settings.PGDATABASE,
        user=settings.PGUSER,
        password=settings.PGPASSWORD
    )
    print(f"Database connection pool initialized: {settings.PGDATABASE}@{settings.PGHOST}:{settings.PGPORT}")


def close_db_pool():
    """Close database connection pool"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        print("Database connection pool closed")


@contextmanager
def get_db_connection():
    """Get a database connection from the pool"""
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)
