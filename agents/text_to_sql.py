from agents.llm_client import llm
from few_shot_examples.examples import examples

# Build few-shot prompt from Python examples
FEW_SHOT_PROMPT = "\n".join(
    [f"Q: {ex['query']}\nSQL: {ex['sql']}" for ex in examples]
)

# PostgreSQL-compatible schema
SCHEMA = """
Schema:
Table company(company_id SERIAL PRIMARY KEY, name TEXT, ticker TEXT, country TEXT, industry TEXT)
Table fiscal_period(period_id SERIAL PRIMARY KEY, company_id INT, fiscal_year INT, fiscal_quarter TEXT, start_date DATE, end_date DATE)
Table statement(statement_id SERIAL PRIMARY KEY, period_id INT, statement_type TEXT, currency TEXT, units TEXT)
Table line_item(line_item_id SERIAL PRIMARY KEY, name TEXT, normalized_code TEXT, category TEXT, description TEXT)
Table financial_fact(fact_id SERIAL PRIMARY KEY, statement_id INT, line_item_id INT, value NUMERIC, units TEXT, note TEXT, source_page INT)
"""

SYSTEM_PROMPT = f"""
You are a PostgreSQL SQL assistant. Generate **valid PostgreSQL queries only**.

Rules:
1. Output ONLY the SQL query. No explanations, no markdown, no text, no repeating the question.
2. Prefer simple, readable queries that answer the question correctly.
3. Use aggregates (SUM, AVG, MIN, MAX) when needed.
4. Use COALESCE(column,0) in SUM to avoid NULLs.
5. Avoid window functions unless strictly necessary.
6. All selected columns must be aggregated or in GROUP BY.
7. Use clear aliases (e.g., total_assets_prev, total_assets_curr, equity_change).
8. For comparisons over periods, prefer WITH clauses.
9. Follow PostgreSQL syntax strictly.

Database schema:
{SCHEMA}

Follow this schema strictly. Do not assume any other tables or columns exist. Do not invent columns.
"""

def text_to_sql_agent(state):
    user_query = state["messages"][-1]
    
    prompt = f"""{SYSTEM_PROMPT}

Few-shot examples:
{FEW_SHOT_PROMPT}

Q: {user_query}
SQL:"""
    
    response = llm.invoke(prompt)
    sql_raw = response.content.strip()
    
    # Strip anything before the first "SELECT" and after the last semicolon
    select_index = sql_raw.lower().find("select")
    if select_index == -1:
        raise ValueError("No SELECT statement found in LLM output")
    
    sql_clean = sql_raw[select_index:]
    
    # Ensure it ends with a semicolon
    if not sql_clean.strip().endswith(";"):
        sql_clean += ";"
    
    return {"sql_query": sql_clean}