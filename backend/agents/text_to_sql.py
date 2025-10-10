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
You are an expert financial SQL code generator for PostgreSQL. 
Your task is to convert **any natural language question** about a company's financial statements into an **optimized SQL query** using the schema described below. 
Output **ONLY the raw SQL query**, without markdown, comments, or extra text.

⚡ Database Schema Overview:

1. company (Metadata about companies)
- company_id SERIAL PRIMARY KEY
- name TEXT NOT NULL
- ticker TEXT UNIQUE
- country TEXT
- industry TEXT

2. fiscal_period (Metadata about time periods)
- period_id SERIAL PRIMARY KEY
- company_id INT REFERENCES company(company_id)
- fiscal_year INT NOT NULL
- fiscal_quarter TEXT ('Q1','Q2','Q3','Q4','FY')
- period_type TEXT ('ANNUAL', 'QUARTERLY', 'TRAILING_12M')
- start_date DATE
- end_date DATE
- UNIQUE(company_id, fiscal_year, fiscal_quarter)

3. statement (Financial statement metadata)
- statement_id SERIAL PRIMARY KEY
- period_id INT REFERENCES fiscal_period(period_id)
- statement_type TEXT ('INCOME', 'BALANCE', 'CASH_FLOW', 'RATIOS')
- currency TEXT DEFAULT 'INR'
- units TEXT DEFAULT 'CRORES'

4. line_item (Financial line items)
- line_item_id SERIAL PRIMARY KEY
- name TEXT
- normalized_code TEXT UNIQUE
- statement_category TEXT ('ASSET','LIABILITY','REVENUE','EXPENSE','CF_OPERATING','PROFITABILITY_RATIO','P&L_MISC','BALANCE_MISC')
- description TEXT

5. financial_fact (The fact table with actual values)
- fact_id SERIAL PRIMARY KEY
- statement_id INT REFERENCES statement(statement_id)
- line_item_id INT REFERENCES line_item(line_item_id)
- value NUMERIC
- note TEXT
- source_page INT

⚡ Guidelines for SQL Generation:

1. Always filter by **company** and optionally by **fiscal_year/fiscal_quarter** based on the user query.
2. Join tables appropriately: `financial_fact` → `statement` → `fiscal_period` → `company` and `financial_fact` → `line_item`.
3. If the query asks for a particular **statement type**, filter on `statement.statement_type`.
4. If the query asks for a **line item or category**, filter on `line_item.name` or `line_item.statement_category`.
5. If multiple periods match (e.g., multiple quarterly periods), select the one(s) relevant to the question (e.g., last FY, or trailing 12M).
6. For **yearly totals**, sum the relevant line items for the fiscal year. For quarterly, select the quarter requested.
7. For **ratios** or computed KPIs, select from `line_item.statement_category = 'RATIO'`.
8. For **trend or volatility analysis**, calculate standard deviation or difference across quarterly values using `STDDEV` or arithmetic differences on `value`.
9. For comparisons like YoY or QoQ:
   - Use joins on fiscal_period to get previous year or previous quarter values.
   - Calculate differences using arithmetic operations.
10. For top/bottom performers or largest movements:
    - Order by `value` or calculated difference
    - Use `LIMIT` if required
11. Always return results with:
    - `company.name` and `fiscal_period.fiscal_year`/`fiscal_quarter` when relevant
    - `line_item.name` and/or `statement_category`
    - `value` or calculated fields
12. If the query is unrelated to finance or SQL, respond naturally instead of generating SQL.

Use only these tables: `company`, `fiscal_period`, `statement`, `line_item`, `financial_fact`.


SQL Query:
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