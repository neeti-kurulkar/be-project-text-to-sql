"""
Text-to-SQL Agent for HUL Financial Data
Uses Llama 3.3 70B with Groq API and Few-Shot Prompting
"""

import os
from typing import TypedDict, Annotated
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Build PostgreSQL connection string from environment variables
DATABASE_URI = f"postgresql://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}:{os.getenv('PGPORT')}/{os.getenv('PGDATABASE')}"

# Initialize Groq LLM (Llama 3.3 70B)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv('GROQ_API_KEY')
)

# Initialize Database
db = SQLDatabase.from_uri(DATABASE_URI)

# ============================================================================
# FEW-SHOT EXAMPLES - Based on Actual HUL Data Structure
# ============================================================================

few_shot_examples = [
    {
        "question": "What is the revenue variance between 2022 and 2023?",
        "sql_query": """
SELECT 
    c.name as company_name,
    MAX(CASE WHEN fp.fiscal_year = 2022 THEN ff.value END) as revenue_2022,
    MAX(CASE WHEN fp.fiscal_year = 2023 THEN ff.value END) as revenue_2023,
    MAX(CASE WHEN fp.fiscal_year = 2023 THEN ff.value END) - 
    MAX(CASE WHEN fp.fiscal_year = 2022 THEN ff.value END) as absolute_variance,
    ROUND(((MAX(CASE WHEN fp.fiscal_year = 2023 THEN ff.value END) - 
            MAX(CASE WHEN fp.fiscal_year = 2022 THEN ff.value END)) / 
            NULLIF(MAX(CASE WHEN fp.fiscal_year = 2022 THEN ff.value END), 0)) * 100, 2) as variance_percentage
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN company c ON fp.company_id = c.company_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code = 'HUL_PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET'
    AND s.statement_type = 'PROFIT_LOSS'
    AND fp.fiscal_year IN (2022, 2023)
GROUP BY c.name;
"""
    },
    {
        "question": "Show me the trend of net cash from operating activities over all years",
        "sql_query": """
SELECT 
    c.name as company_name,
    fp.fiscal_year,
    li.name as metric,
    ff.value,
    s.currency,
    s.units,
    LAG(ff.value) OVER (ORDER BY fp.fiscal_year) as previous_year,
    ff.value - LAG(ff.value) OVER (ORDER BY fp.fiscal_year) as yoy_change,
    ROUND(((ff.value - LAG(ff.value) OVER (ORDER BY fp.fiscal_year)) / 
           NULLIF(LAG(ff.value) OVER (ORDER BY fp.fiscal_year), 0)) * 100, 2) as yoy_change_pct
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN company c ON fp.company_id = c.company_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code = 'HUL_CASH_FLOW_NET_CASH_FROM_OPERATING_ACTIVITIES'
    AND s.statement_type = 'CASH_FLOW'
ORDER BY fp.fiscal_year;
"""
    },
    {
        "question": "Compare the current ratio across all years",
        "sql_query": """
SELECT 
    c.name as company_name,
    MAX(CASE WHEN fp.fiscal_year = 2021 THEN ff.value END) as year_2021,
    MAX(CASE WHEN fp.fiscal_year = 2022 THEN ff.value END) as year_2022,
    MAX(CASE WHEN fp.fiscal_year = 2023 THEN ff.value END) as year_2023,
    MAX(CASE WHEN fp.fiscal_year = 2024 THEN ff.value END) as year_2024,
    MAX(CASE WHEN fp.fiscal_year = 2025 THEN ff.value END) as year_2025,
    ROUND(AVG(ff.value), 2) as avg_ratio,
    ROUND(MIN(ff.value), 2) as min_ratio,
    ROUND(MAX(ff.value), 2) as max_ratio
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN company c ON fp.company_id = c.company_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code = 'HUL_RATIOS_CURRENT_RATIO'
    AND s.statement_type = 'RATIOS'
GROUP BY c.name;
"""
    },
    {
        "question": "What is the profit margin trend over the years?",
        "sql_query": """
SELECT 
    c.name as company_name,
    fp.fiscal_year,
    li.name as metric,
    ff.value as net_profit_margin,
    LAG(ff.value, 1) OVER (ORDER BY fp.fiscal_year) as prev_year_margin,
    ff.value - LAG(ff.value, 1) OVER (ORDER BY fp.fiscal_year) as margin_change,
    ROUND(AVG(ff.value) OVER (), 2) as avg_margin_all_years
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN company c ON fp.company_id = c.company_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code = 'HUL_RATIOS_NET_PROFIT_MARGIN'
    AND s.statement_type = 'RATIOS'
ORDER BY fp.fiscal_year;
"""
    },
    {
        "question": "Show me total assets growth from 2021 to 2025",
        "sql_query": """
SELECT 
    c.name as company_name,
    fp.fiscal_year,
    li.name as metric,
    ff.value as total_assets,
    s.units,
    LAG(ff.value, 1) OVER (ORDER BY fp.fiscal_year) as prev_year_assets,
    ff.value - LAG(ff.value, 1) OVER (ORDER BY fp.fiscal_year) as yoy_growth,
    ROUND(((ff.value - LAG(ff.value, 1) OVER (ORDER BY fp.fiscal_year)) / 
           NULLIF(LAG(ff.value, 1) OVER (ORDER BY fp.fiscal_year), 0)) * 100, 2) as yoy_growth_pct,
    ROUND(((ff.value - FIRST_VALUE(ff.value) OVER (ORDER BY fp.fiscal_year)) / 
           NULLIF(FIRST_VALUE(ff.value) OVER (ORDER BY fp.fiscal_year), 0)) * 100, 2) as cumulative_growth_pct
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN company c ON fp.company_id = c.company_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.normalized_code = 'HUL_BALANCE_TOTAL_ASSETS'
    AND s.statement_type = 'BALANCE'
ORDER BY fp.fiscal_year;
"""
    },
    {
        "question": "Compare debt equity ratio with return on net worth",
        "sql_query": """
WITH debt_equity AS (
    SELECT 
        fp.fiscal_year,
        ff.value as debt_equity_ratio
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_RATIOS_DEBT_EQUITY_RATIO'
        AND s.statement_type = 'RATIOS'
),
return_metrics AS (
    SELECT 
        fp.fiscal_year,
        ff.value as return_on_net_worth
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_RATIOS_RETURN_ON_NET_WORTH'
        AND s.statement_type = 'RATIOS'
)
SELECT 
    de.fiscal_year,
    de.debt_equity_ratio,
    rm.return_on_net_worth,
    ROUND(de.debt_equity_ratio * rm.return_on_net_worth, 2) as leverage_adjusted_return
FROM debt_equity de
JOIN return_metrics rm ON de.fiscal_year = rm.fiscal_year
ORDER BY de.fiscal_year;
"""
    },
    {
        "question": "What are the key profitability metrics for 2024?",
        "sql_query": """
SELECT 
    c.name as company_name,
    fp.fiscal_year,
    li.name as metric,
    ff.value,
    ROUND(AVG(ff.value) OVER (PARTITION BY li.line_item_id), 2) as avg_across_years,
    ff.value - AVG(ff.value) OVER (PARTITION BY li.line_item_id) as variance_from_avg
FROM financial_fact ff
JOIN statement s ON ff.statement_id = s.statement_id
JOIN fiscal_period fp ON s.period_id = fp.period_id
JOIN company c ON fp.company_id = c.company_id
JOIN line_item li ON ff.line_item_id = li.line_item_id
WHERE li.statement_category = 'RATIO'
    AND li.normalized_code IN (
        'HUL_RATIOS_NET_PROFIT_MARGIN',
        'HUL_RATIOS_OPERATING_PROFIT_MARGIN',
        'HUL_RATIOS_RETURN_ON_NET_WORTH',
        'HUL_RATIOS_RETURN_ON_CAPITAL_EMPLOYED',
        'HUL_RATIOS_RETURN_ON_ASSETS_EXCLUDING_REVALUATIONS'
    )
    AND s.statement_type = 'RATIOS'
    AND fp.fiscal_year = 2024
ORDER BY li.name;
"""
    },
    {
        "question": "Analyze working capital efficiency over time",
        "sql_query": """
WITH current_assets AS (
    SELECT 
        fp.fiscal_year,
        ff.value as current_assets
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_BALANCE_TOTAL_CURRENT_ASSETS'
        AND s.statement_type = 'BALANCE'
),
current_liabilities AS (
    SELECT 
        fp.fiscal_year,
        ff.value as current_liabilities
    FROM financial_fact ff
    JOIN statement s ON ff.statement_id = s.statement_id
    JOIN fiscal_period fp ON s.period_id = fp.period_id
    JOIN line_item li ON ff.line_item_id = li.line_item_id
    WHERE li.normalized_code = 'HUL_BALANCE_TOTAL_CURRENT_LIABILITIES'
        AND s.statement_type = 'BALANCE'
)
SELECT 
    ca.fiscal_year,
    ca.current_assets,
    cl.current_liabilities,
    ca.current_assets - cl.current_liabilities as working_capital,
    ROUND(ca.current_assets / NULLIF(cl.current_liabilities, 0), 2) as current_ratio,
    LAG(ca.current_assets - cl.current_liabilities) OVER (ORDER BY ca.fiscal_year) as prev_year_wc,
    (ca.current_assets - cl.current_liabilities) - 
    LAG(ca.current_assets - cl.current_liabilities) OVER (ORDER BY ca.fiscal_year) as wc_change
FROM current_assets ca
JOIN current_liabilities cl ON ca.fiscal_year = cl.fiscal_year
ORDER BY ca.fiscal_year;
"""
    }
]

# ============================================================================
# SCHEMA CONTEXT
# ============================================================================

SCHEMA_DESCRIPTION = """
Database: HUL (Hindustan Unilever Limited) Financial Data (2021-2025)

Tables:
1. company: (company_id, name, ticker, country, industry)
   - Single company: HUL (ID: 1)

2. fiscal_period: (period_id, company_id, fiscal_year, fiscal_quarter, period_type, start_date, end_date)
   - fiscal_year: 2021, 2022, 2023, 2024, 2025
   - fiscal_quarter: 'FY' (Full Year) - all data is ANNUAL
   - period_type: 'ANNUAL'

3. statement: (statement_id, period_id, statement_type, currency, units)
   - statement_type: 'BALANCE', 'CASH_FLOW', 'RATIOS', 'PROFIT_LOSS'
   - currency: 'INR'
   - units: 'CRORES'

4. line_item: (line_item_id, name, normalized_code, statement_category, description)
   - Categories: ASSET, LIABILITY, REVENUE, EXPENSE, RATIO, CF_OPERATING, CF_INVESTING, CF_FINANCING
   - Key normalized_codes examples:
     * Revenue: HUL_PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET
     * Profit: HUL_PROFIT_LOSS_PROFIT_LOSS_FOR_THE_PERIOD
     * Assets: HUL_BALANCE_TOTAL_ASSETS
     * Cash Flow: HUL_CASH_FLOW_NET_CASH_FROM_OPERATING_ACTIVITIES
     * Ratios: HUL_RATIOS_NET_PROFIT_MARGIN, HUL_RATIOS_CURRENT_RATIO, HUL_RATIOS_DEBT_EQUITY_RATIO

5. financial_fact: (fact_id, statement_id, line_item_id, value, note, source_page)
   - Central fact table with all financial values

Join Pattern:
financial_fact -> statement -> fiscal_period -> company
financial_fact -> line_item
"""

# ============================================================================
# PROMPT TEMPLATE
# ============================================================================

example_prompt = PromptTemplate(
    input_variables=["question", "sql_query"],
    template="Question: {question}\nSQL:\n{sql_query}\n"
)

few_shot_prompt = FewShotPromptTemplate(
    examples=few_shot_examples,
    example_prompt=example_prompt,
    prefix=f"""You are an expert PostgreSQL query generator for HUL financial data.

{SCHEMA_DESCRIPTION}

CRITICAL RULES:
1. Return ONLY the SQL query, no explanations or markdown
2. Use normalized_code from line_item table (starts with 'HUL_')
3. Always join: financial_fact -> statement -> fiscal_period -> company -> line_item
4. Include contextual data: prior years, YoY changes, percentages, averages
5. Use window functions (LAG, LEAD, FIRST_VALUE) for trends
6. Use CASE statements for year pivots
7. Handle NULLs with NULLIF in divisions
8. Round percentages to 2 decimals
9. All years are ANNUAL (period_type = 'ANNUAL')
10. Values are in INR Crores

Examples:
""",
    suffix="Question: {question}\nSQL:",
    input_variables=["question"]
)

# ============================================================================
# LANGGRAPH STATE
# ============================================================================

class AgentState(TypedDict):
    question: str
    sql_query: str
    iteration: int
    error: str

# ============================================================================
# NODES
# ============================================================================

def generate_sql(state: AgentState) -> AgentState:
    """Generate SQL query using few-shot prompting."""
    question = state["question"]
    
    try:
        prompt = few_shot_prompt.format(question=question)
        response = llm.invoke(prompt)
        
        # Clean SQL query
        sql_query = response.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        # Remove any explanatory text before SELECT
        if "SELECT" in sql_query.upper():
            sql_query = sql_query[sql_query.upper().find("SELECT"):]
        
        return {
            **state,
            "sql_query": sql_query,
            "error": ""
        }
    except Exception as e:
        return {
            **state,
            "error": f"Generation Error: {str(e)}"
        }

def validate_sql(state: AgentState) -> AgentState:
    """Validate SQL by attempting a EXPLAIN query."""
    sql_query = state["sql_query"]
    
    try:
        # Try to explain the query (doesn't execute, just validates)
        db.run(f"EXPLAIN {sql_query}")
        return {**state, "error": ""}
    except Exception as e:
        return {
            **state,
            "error": f"Validation Error: {str(e)}",
            "iteration": state.get("iteration", 0) + 1
        }

def fix_sql(state: AgentState) -> AgentState:
    """Fix SQL query based on error."""
    error = state["error"]
    sql_query = state["sql_query"]
    question = state["question"]
    
    fix_prompt = f"""The SQL query has an error. Fix it.

Schema: {SCHEMA_DESCRIPTION}

Question: {question}
Broken SQL: {sql_query}
Error: {error}

Return ONLY the corrected SQL query, no explanations.
Corrected SQL:"""
    
    try:
        response = llm.invoke(fix_prompt)
        fixed_query = response.content.strip().replace("```sql", "").replace("```", "").strip()
        
        if "SELECT" in fixed_query.upper():
            fixed_query = fixed_query[fixed_query.upper().find("SELECT"):]
        
        return {
            **state,
            "sql_query": fixed_query,
            "error": ""
        }
    except Exception as e:
        return {
            **state,
            "error": f"Fix Error: {str(e)}"
        }

# ============================================================================
# CONDITIONAL EDGES
# ============================================================================

def should_retry(state: AgentState) -> str:
    """Decide whether to retry."""
    if state.get("error") and state.get("iteration", 0) < 2:
        return "fix"
    elif state.get("error"):
        return "end"
    return "end"

# ============================================================================
# BUILD GRAPH
# ============================================================================

def build_graph():
    """Build the agent workflow."""
    workflow = StateGraph(AgentState)
    
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate_sql", validate_sql)
    workflow.add_node("fix_sql", fix_sql)
    
    workflow.set_entry_point("generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")
    
    workflow.add_conditional_edges(
        "validate_sql",
        should_retry,
        {
            "fix": "fix_sql",
            "end": END
        }
    )
    
    workflow.add_edge("fix_sql", "validate_sql")
    
    return workflow.compile()

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def generate_sql_query(question: str) -> str:
    """
    Generate SQL query from natural language question.
    
    Args:
        question: Natural language question about HUL financial data
        
    Returns:
        SQL query string
    """
    graph = build_graph()
    
    initial_state = {
        "question": question,
        "sql_query": "",
        "iteration": 0,
        "error": ""
    }
    
    result = graph.invoke(initial_state)
    
    if result.get("error"):
        return f"-- Error generating SQL: {result['error']}\n-- Question: {question}"
    
    return result["sql_query"]

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Test queries
    test_questions = [
        "What is the revenue variance between 2022 and 2023?",
        "Show me the net profit margin trend over all years",
        "Compare current ratio and quick ratio across years",
        "How has total assets grown from 2021 to 2025?",
        "What are the key profitability ratios for 2024?"
    ]
    
    print("HUL Financial Data - Text-to-SQL Agent")
    print("=" * 80)
    
    question = "How has total assets grown from 2021 to 2025?"

    print(f"\n\nQuestion: {question}")
    print("-" * 80)
        
    sql_query = generate_sql_query(question)
    print(sql_query)