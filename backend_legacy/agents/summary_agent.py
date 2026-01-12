"""
Summary Agent
Generates comprehensive financial summary of HUL across all available data
"""

import os
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


class SummaryAgent:
    """
    Agent that generates a comprehensive financial summary of the company
    by analyzing all available data across multiple years and metrics.
    """
    
    def __init__(self):
        """Initialize the Summary Agent."""
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            api_key=os.getenv('GROQ_API_KEY')
        )
        
        # Build database connection
        DATABASE_URI = f"postgresql://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}:{os.getenv('PGPORT')}/{os.getenv('PGDATABASE')}"
        self.db = SQLDatabase.from_uri(DATABASE_URI)
    
    def _fetch_key_metrics(self) -> dict:
        """Fetch key financial metrics for summary."""
        
        queries = {
            "revenue": """
                SELECT fp.fiscal_year, ff.value as revenue
                FROM financial_fact ff
                JOIN statement s ON ff.statement_id = s.statement_id
                JOIN fiscal_period fp ON s.period_id = fp.period_id
                JOIN line_item li ON ff.line_item_id = li.line_item_id
                WHERE li.normalized_code = 'HUL_PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET'
                    AND s.statement_type = 'PROFIT_LOSS'
                ORDER BY fp.fiscal_year;
            """,
            "profit": """
                SELECT fp.fiscal_year, ff.value as net_profit
                FROM financial_fact ff
                JOIN statement s ON ff.statement_id = s.statement_id
                JOIN fiscal_period fp ON s.period_id = fp.period_id
                JOIN line_item li ON ff.line_item_id = li.line_item_id
                WHERE li.normalized_code = 'HUL_PROFIT_LOSS_PROFIT_LOSS_FOR_THE_PERIOD'
                    AND s.statement_type = 'PROFIT_LOSS'
                ORDER BY fp.fiscal_year;
            """,
            "assets": """
                SELECT fp.fiscal_year, ff.value as total_assets
                FROM financial_fact ff
                JOIN statement s ON ff.statement_id = s.statement_id
                JOIN fiscal_period fp ON s.period_id = fp.period_id
                JOIN line_item li ON ff.line_item_id = li.line_item_id
                WHERE li.normalized_code = 'HUL_BALANCE_TOTAL_ASSETS'
                    AND s.statement_type = 'BALANCE'
                ORDER BY fp.fiscal_year;
            """,
            "operating_cash_flow": """
                SELECT fp.fiscal_year, ff.value as operating_cf
                FROM financial_fact ff
                JOIN statement s ON ff.statement_id = s.statement_id
                JOIN fiscal_period fp ON s.period_id = fp.period_id
                JOIN line_item li ON ff.line_item_id = li.line_item_id
                WHERE li.normalized_code = 'HUL_CASH_FLOW_NET_CASH_FROM_OPERATING_ACTIVITIES'
                    AND s.statement_type = 'CASH_FLOW'
                ORDER BY fp.fiscal_year;
            """,
            "key_ratios": """
                SELECT 
                    fp.fiscal_year,
                    MAX(CASE WHEN li.normalized_code = 'HUL_RATIOS_NET_PROFIT_MARGIN' THEN ff.value END) as npm,
                    MAX(CASE WHEN li.normalized_code = 'HUL_RATIOS_RETURN_ON_NET_WORTH' THEN ff.value END) as roe,
                    MAX(CASE WHEN li.normalized_code = 'HUL_RATIOS_CURRENT_RATIO' THEN ff.value END) as current_ratio,
                    MAX(CASE WHEN li.normalized_code = 'HUL_RATIOS_DEBT_EQUITY_RATIO' THEN ff.value END) as de_ratio
                FROM financial_fact ff
                JOIN statement s ON ff.statement_id = s.statement_id
                JOIN fiscal_period fp ON s.period_id = fp.period_id
                JOIN line_item li ON ff.line_item_id = li.line_item_id
                WHERE s.statement_type = 'RATIOS'
                    AND li.normalized_code IN (
                        'HUL_RATIOS_NET_PROFIT_MARGIN',
                        'HUL_RATIOS_RETURN_ON_NET_WORTH',
                        'HUL_RATIOS_CURRENT_RATIO',
                        'HUL_RATIOS_DEBT_EQUITY_RATIO'
                    )
                GROUP BY fp.fiscal_year
                ORDER BY fp.fiscal_year;
            """
        }
        
        data = {}
        try:
            for key, query in queries.items():
                result = self.db.run(query)
                # Convert to pandas for easier processing
                data[key] = result
        except Exception as e:
            print(f"Error fetching metrics: {str(e)}")
            data = {}
        
        return data
    
    def generate_summary(self) -> dict:
        """
        Generate comprehensive financial summary.
        
        Returns:
            Dictionary with summary content and error status
        """
        try:
            # Fetch key metrics
            metrics_data = self._fetch_key_metrics()
            
            if not metrics_data:
                return {
                    "summary": None,
                    "error": "Unable to fetch financial data"
                }
            
            # Build prompt for LLM
            prompt = f"""You are a financial analyst creating a comprehensive summary of Hindustan Unilever Limited (HUL) based on their financial data from 2021-2025.

FINANCIAL DATA:

Revenue Trend:
{metrics_data.get('revenue', 'N/A')}

Net Profit Trend:
{metrics_data.get('profit', 'N/A')}

Total Assets:
{metrics_data.get('assets', 'N/A')}

Operating Cash Flow:
{metrics_data.get('operating_cash_flow', 'N/A')}

Key Financial Ratios:
{metrics_data.get('key_ratios', 'N/A')}

Create a comprehensive financial summary with the following structure:

# Hindustan Unilever Limited - Financial Summary (2021-2025)

## Company Overview
[Brief introduction to HUL's business and market position]

## Financial Performance Highlights

### Revenue Performance
[Analysis of revenue trends, growth rates, CAGR]

### Profitability
[Net profit trends, margin analysis, profitability drivers]

### Asset Base
[Asset growth, composition, efficiency]

### Cash Flow
[Operating cash flow trends, cash generation capability]

## Key Financial Ratios

### Profitability Ratios
[Net profit margin, ROE analysis]

### Liquidity Ratios
[Current ratio, working capital management]

### Leverage Ratios
[Debt-equity ratio, financial stability]

## Strengths
[3-4 bullet points of key strengths]

## Areas of Attention
[2-3 bullet points of areas to monitor]

## Overall Assessment
[1-2 paragraph executive summary of financial health and outlook]

---

INSTRUCTIONS:
- Use actual numbers from the data provided
- Calculate growth rates and key metrics
- Be specific with percentages and absolute values
- Keep language professional but accessible
- Focus on trends and insights, not just numbers
- Use markdown formatting with headers and bullets
- Total length: 400-600 words

Generate the summary now:"""
            
            # Get summary from LLM
            response = self.llm.invoke(prompt)
            summary_content = response.content.strip()
            
            return {
                "summary": summary_content,
                "error": None
            }
            
        except Exception as e:
            return {
                "summary": None,
                "error": f"Summary generation error: {str(e)}"
            }


if __name__ == "__main__":
    # Test the agent
    agent = SummaryAgent()
    
    print("Generating HUL Financial Summary...")
    result = agent.generate_summary()
    
    if result["error"]:
        print(f"Error: {result['error']}")
    else:
        print("\n" + "="*80)
        print("FINANCIAL SUMMARY")
        print("="*80)
        print(result["summary"])