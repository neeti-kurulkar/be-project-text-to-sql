import re

def validate_sql(sql):
    """
    Basic SQL validation for PostgreSQL:
    - Only allow SELECT queries or CTEs (WITH ... SELECT ...)
    - Block dangerous operations
    """
    sql = sql.strip()
    
    # Accept queries starting with SELECT or WITH
    if not (sql.lower().startswith("select") or sql.lower().startswith("with")):
        raise ValueError("Only SELECT queries or CTE-based SELECT queries are allowed.")

    # Forbidden keywords
    forbidden = [
        "delete", "drop", "update", "insert", "truncate", "alter", "grant", "revoke"
    ]
    if any(word in sql.lower() for word in forbidden):
        raise ValueError("Query contains forbidden operations.")

    # remove extra backticks or triple quotes
    sql = re.sub(r"```", "", sql)
    return sql
