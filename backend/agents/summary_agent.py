from agents.llm_client import llm
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()  # Load DB credentials from .env

DB_PARAMS = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD")
}

def query_db(query):
    """Executes a SQL query on the PostgreSQL database and returns a DataFrame."""
    conn = psycopg2.connect(**DB_PARAMS)
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df

def company_summary_agent(state=None):
    """
    Generates a high-level business summary of the company based on the database,
    including company info, fiscal year range, and key financial metrics.
    """
    # Company metadata
    company_df = query_db("""
        SELECT company_id, name, ticker, country, industry
        FROM company
        LIMIT 1
    """)
    company_info = company_df.iloc[0].to_dict() if not company_df.empty else {
        "name": "Unknown", "ticker": "", "country": "", "industry": ""
    }

    # Fiscal year range
    years_df = query_db("""
        SELECT MIN(fiscal_year) AS start_year, MAX(fiscal_year) AS end_year
        FROM fiscal_period
    """)
    start_year = years_df.at[0, "start_year"] if not years_df.empty else "N/A"
    end_year = years_df.at[0, "end_year"] if not years_df.empty else "N/A"

    # Aggregated financial metrics
    revenue_df = query_db("""
        SELECT fp.fiscal_year, SUM(ff.value) AS total_revenue
        FROM financial_fact ff
        JOIN line_item li ON ff.line_item_id = li.line_item_id
        JOIN statement s ON ff.statement_id = s.statement_id
        JOIN fiscal_period fp ON s.period_id = fp.period_id
        WHERE li.normalized_code='REV' AND s.statement_type='income'
        GROUP BY fp.fiscal_year
        ORDER BY fp.fiscal_year
    """)

    net_income_df = query_db("""
        SELECT fp.fiscal_year, SUM(ff.value) AS net_income
        FROM financial_fact ff
        JOIN line_item li ON ff.line_item_id = li.line_item_id
        JOIN statement s ON ff.statement_id = s.statement_id
        JOIN fiscal_period fp ON s.period_id = fp.period_id
        WHERE li.normalized_code='NI' AND s.statement_type='income'
        GROUP BY fp.fiscal_year
        ORDER BY fp.fiscal_year
    """)

    total_assets_df = query_db("""
        SELECT fp.fiscal_year, SUM(ff.value) AS total_assets
        FROM financial_fact ff
        JOIN line_item li ON ff.line_item_id = li.line_item_id
        JOIN statement s ON ff.statement_id = s.statement_id
        JOIN fiscal_period fp ON s.period_id = fp.period_id
        WHERE li.normalized_code='TA' AND s.statement_type='balance'
        GROUP BY fp.fiscal_year
        ORDER BY fp.fiscal_year
    """)

    # Prepare aggregated data for LLM
    summary_data = {
        "Company Info": company_info,
        "Fiscal Years": {"start_year": start_year, "end_year": end_year},
        "Revenue by Year": revenue_df.to_dict(orient="records"),
        "Net Income by Year": net_income_df.to_dict(orient="records"),
        "Total Assets by Year": total_assets_df.to_dict(orient="records")
    }

    prompt = f"""
You are a financial analyst reviewing a company from a stakeholder perspective.

Company Info:
{company_info}
Fiscal Year Range: {start_year} to {end_year}

Based on the following aggregated data:
{summary_data}

Write a high-level business summary (10-15 lines) describing the company's overall financial health and performance trends.
Include the company's growth, profitability, and financial stability.
Use clear, natural business language, and avoid mechanically repeating the numbers.
"""

    response = llm.invoke(prompt)
    return {"summary": response.content}