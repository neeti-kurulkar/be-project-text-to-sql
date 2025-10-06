from agents.llm_client import llm
from few_shot_examples.examples import examples

# ---------------------------------------------------------------------
# 1️⃣ Build Few-shot Prompt
# ---------------------------------------------------------------------
FEW_SHOT_PROMPT = "\n".join(
    [f"Q: {ex['query']}\nSQL: {ex['sql'].strip()}" for ex in examples]
)

# ---------------------------------------------------------------------
# 2️⃣ PostgreSQL-Compatible Schema
# ---------------------------------------------------------------------
SCHEMA = """
Schema:
Table company(
    company_id SERIAL PRIMARY KEY,
    name TEXT,
    ticker TEXT,
    country TEXT,
    industry TEXT
);

Table fiscal_period(
    period_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES company(company_id),
    fiscal_year INT,
    fiscal_quarter TEXT,
    start_date DATE,
    end_date DATE
);

Table statement(
    statement_id SERIAL PRIMARY KEY,
    period_id INT REFERENCES fiscal_period(period_id),
    statement_type TEXT,  -- 'balance', 'cash_flow', 'profit_loss', 'ratios'
    currency TEXT,
    units TEXT
);

Table line_item(
    line_item_id SERIAL PRIMARY KEY,
    name TEXT,
    normalized_code TEXT,
    category TEXT,
    description TEXT
);

Table financial_fact(
    fact_id SERIAL PRIMARY KEY,
    statement_id INT REFERENCES statement(statement_id),
    line_item_id INT REFERENCES line_item(line_item_id),
    value NUMERIC,
    units TEXT,
    note TEXT,
    source_page INT
);
"""

# ---------------------------------------------------------------------
# 3️⃣ System Prompt
# ---------------------------------------------------------------------
SYSTEM_PROMPT = f"""
You are a **PostgreSQL SQL assistant** that generates correct, efficient, and executable SQL queries
for financial analytics. Translate user financial questions into valid SQL queries using the schema below.

⚡ Rules:
1. Output ONLY the SQL query — no explanations, comments, markdown, or quotes.
2. Always follow the schema exactly. Do NOT invent tables or columns.
3. Use table aliases consistently (c, fp, s, ff, li, etc.).
4. Always use COALESCE(column, 0) for numeric aggregations.
5. Prefer simple, readable queries with GROUP BY, ORDER BY, LIMIT, or aggregates where appropriate.
6. Use normalized_code to match financial metrics (e.g., HUL_BALANCE_TOTAL_ASSETS, HUL_PROFIT_LOSS_PROFIT_LOSS_FOR_THE_PERIOD).
7. For time-based comparisons, use fiscal_year/fiscal_quarter properly — do not assume period_id implies order.

📊 Database Schema:

Table **company**
- company_id (PK)
- name
- ticker
- country
- industry

Table **fiscal_period**
- period_id (PK)
- company_id (FK → company)
- fiscal_year
- fiscal_quarter
- start_date
- end_date

Table **statement**
- statement_id (PK)
- period_id (FK → fiscal_period)
- statement_type (balance, income, cash_flow)
- currency
- units

Table **line_item**
- line_item_id (PK)
- name
- normalized_code
- category
- description

Table **financial_fact**
- fact_id (PK)
- statement_id (FK → statement)
- line_item_id (FK → line_item)
- value
- units
- note
- source_page

💡 Key relationships:
- company → fiscal_period → statement → financial_fact → line_item
- Each fiscal_period may have multiple statements.
- Each statement has multiple financial_fact rows, each linked to a line_item.
- Use fiscal_year/fiscal_quarter to handle period-based calculations or comparisons.
- Use normalized_code to identify the exact financial metric.

Always generate queries that:
- Correctly follow joins through these tables.
- Handle year-over-year, growth, or aggregation questions using fiscal_year/fiscal_quarter.
- Aggregate numbers where needed using SUM, AVG, MAX, MIN.
- Only select columns needed to answer the question.
"""


# ---------------------------------------------------------------------
# 4️⃣ Agent Function
# ---------------------------------------------------------------------
def text_to_sql_agent(state):
    """
    LangGraph-compatible agent that converts user questions into SQL queries
    using few-shot prompting and the defined PostgreSQL schema.
    """
    user_query = state["messages"][-1]

    prompt = f"""{SYSTEM_PROMPT}

Few-shot examples:
{FEW_SHOT_PROMPT}

Q: {user_query}
SQL:"""

    response = llm.invoke(prompt)
    sql_raw = response.content.strip()

    # Extract the SQL safely
    select_index = sql_raw.lower().find("select")
    if select_index == -1:
        raise ValueError("No SELECT statement found in LLM output")

    sql_clean = sql_raw[select_index:]
    if not sql_clean.strip().endswith(";"):
        sql_clean += ";"

    return {"sql_query": sql_clean}