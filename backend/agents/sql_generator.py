"""
SQL Generator Agent
Converts natural language questions to SQL queries using few-shot prompting
"""

import os
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from few_shot_examples.examples import FEW_SHOT_EXAMPLES, SCHEMA_DESCRIPTION

load_dotenv()

class SQLGeneratorAgent:
    def __init__(self):
        """Initialize the SQL Generator Agent."""
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.getenv('GROQ_API_KEY')
        )
        
        self.prompt = self._build_prompt()
    
    def _build_prompt(self) -> FewShotPromptTemplate:
        """Build the few-shot prompt template."""
        example_prompt = PromptTemplate(
            input_variables=["question", "sql_query"],
            template="Question: {question}\nSQL:\n{sql_query}\n"
        )
        
        few_shot_prompt = FewShotPromptTemplate(
            examples=FEW_SHOT_EXAMPLES,
            example_prompt=example_prompt,
            prefix=f"""You are an expert PostgreSQL query generator for HUL financial data.

{SCHEMA_DESCRIPTION}

CRITICAL RULES:
1. Return ONLY the SQL query, no explanations or markdown
2. Use normalized_code from line_item table (starts with 'HUL_')
3. Always join: financial_fact -> statement -> fiscal_period -> company -> line_item
4. Include contextual data: prior years, YoY changes, percentages, averages
5. Use window functions (LAG, LEAD, FIRST_VALUE, AVG OVER, RANK) for trends and comparisons
6. Use CASE statements with MAX/GROUP BY for year pivots
7. Use CTEs for complex multi-metric analysis
8. Handle NULLs with NULLIF in divisions
9. Round percentages to 2 decimals, ratios to 2-3 decimals
10. All years are ANNUAL (period_type = 'ANNUAL'), fiscal_year range: 2021-2025
11. Values are in INR Crores
12. For comparisons, include both absolute and percentage changes
13. For trends, include cumulative growth from base year
14. For composition analysis, include % of total
15. Add derived metrics when relevant (e.g., working capital = current assets - current liabilities)

Common Query Patterns:
- Year comparison: Use CASE with MAX(CASE WHEN fiscal_year = X THEN value END)
- Trends: Use LAG() OVER (ORDER BY fiscal_year) for YoY
- Cumulative: Use FIRST_VALUE() OVER (ORDER BY fiscal_year)
- Multi-metric: Use CTEs to join different metrics
- Composition: Calculate % using value / SUM(value) OVER (PARTITION BY...)
- Ranking: Use RANK() OVER (ORDER BY value DESC)

Examples:
""",
            suffix="Question: {question}\nSQL:",
            input_variables=["question"]
        )
        
        return few_shot_prompt
    
    def generate(self, question: str) -> dict:
        """
        Generate SQL query from natural language question.
        
        Args:
            question: Natural language question about financial data
            
        Returns:
            Dictionary with 'sql_query' and 'error' keys
        """
        try:
            prompt = self.prompt.format(question=question)
            response = self.llm.invoke(prompt)
            
            # Clean SQL query
            sql_query = response.content.strip()
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            # Remove any explanatory text before SELECT/WITH
            if "SELECT" in sql_query.upper():
                select_pos = sql_query.upper().find("SELECT")
                with_pos = sql_query.upper().find("WITH")
                
                if with_pos != -1 and (select_pos == -1 or with_pos < select_pos):
                    sql_query = sql_query[with_pos:]
                elif select_pos != -1:
                    sql_query = sql_query[select_pos:]
            
            return {
                "sql_query": sql_query,
                "error": None
            }
            
        except Exception as e:
            return {
                "sql_query": None,
                "error": f"SQL Generation Error: {str(e)}"
            }
    
    def fix_query(self, question: str, broken_sql: str, error: str) -> dict:
        """
        Attempt to fix a broken SQL query.
        
        Args:
            question: Original question
            broken_sql: The SQL that failed
            error: Error message
            
        Returns:
            Dictionary with fixed 'sql_query' and 'error' keys
        """
        fix_prompt = f"""The SQL query has an error. Fix it.

Schema: {SCHEMA_DESCRIPTION}

Question: {question}
Broken SQL: {broken_sql}
Error: {error}

Common mistakes:
- Using wrong table/column names
- Missing JOINs
- Incorrect normalized_code values (must start with HUL_)
- Division by zero (use NULLIF)
- Syntax errors

Return ONLY the corrected SQL query, no explanations.
Corrected SQL:"""
        
        try:
            response = self.llm.invoke(fix_prompt)
            fixed_query = response.content.strip().replace("```sql", "").replace("```", "").strip()
            
            # Extract SQL portion
            if "SELECT" in fixed_query.upper():
                select_pos = fixed_query.upper().find("SELECT")
                with_pos = fixed_query.upper().find("WITH")
                
                if with_pos != -1 and (select_pos == -1 or with_pos < select_pos):
                    fixed_query = fixed_query[with_pos:]
                elif select_pos != -1:
                    fixed_query = fixed_query[select_pos:]
            
            return {
                "sql_query": fixed_query,
                "error": None
            }
            
        except Exception as e:
            return {
                "sql_query": None,
                "error": f"Fix Error: {str(e)}"
            }


if __name__ == "__main__":
    # Test the agent
    agent = SQLGeneratorAgent()
    
    test_question = "What is the revenue variance between 2022 and 2023?"
    result = agent.generate(test_question)
    
    print("Question:", test_question)
    print("\nGenerated SQL:")
    print(result["sql_query"])
    
    if result["error"]:
        print("\nError:", result["error"])