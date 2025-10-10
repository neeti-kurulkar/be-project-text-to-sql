import os
import psycopg2
from utils.sql_validator import validate_sql
from dotenv import load_dotenv

load_dotenv()  # Load DB credentials

def query_executor_agent(state):
    conn = psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    )
    cursor = conn.cursor()
    try:
        # Validate and clean SQL before executing
        sql_query = validate_sql(state["sql_query"])
        cursor.execute(sql_query)

        # If SELECT, fetch results
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
        else:
            conn.commit()  # For INSERT/UPDATE/DELETE
            result = {"status": "success", "rows_affected": cursor.rowcount}

    except Exception as e:
        result = {"error": str(e)}
    finally:
        cursor.close()
        conn.close()

    return {"query_result": result}