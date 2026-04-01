import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# 🔥 Load .env manually
load_dotenv()

# Connection pool
connection_pool = None


def init_db_pool():
    """Initialize database connection pool"""
    global connection_pool

    if connection_pool is None:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "financial_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "root")
        )

        print(f"✅ DB Connected: {os.getenv('DB_NAME')} @ {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")


def close_db_pool():
    """Close database connection pool"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        print("Database connection pool closed")


@contextmanager
def get_db_connection():
    """Get a database connection from the pool"""
    global connection_pool

    if connection_pool is None:
        init_db_pool()  # 🔥 AUTO INIT if not initialized

    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)