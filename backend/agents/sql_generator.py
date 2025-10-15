"""
SQL Generator Agent
Converts natural language questions to SQL queries using few-shot prompting
"""

import os
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from few_shot_examples.examples import FEW_SHOT_EXAMPLES, SCHEMA_DESCRIPTION
from few_shot_examples.semantic_selector import get_selector

load_dotenv()

class SQLGeneratorAgent:
    def __init__(self, model_name: str = None, use_semantic_selection: bool = True, max_examples: int = 5, provider: str = 'huggingface'):
        """
        Initialize the SQL Generator Agent.

        Args:
            model_name: Model name
                       For Groq: 'llama-3.3-70b-versatile', 'mixtral-8x7b-32768'
                       For HuggingFace: 'meta-llama/Meta-Llama-3-70B-Instruct', 'mistralai/Mixtral-8x7B-Instruct-v0.1'
                       If None, uses default for provider
            use_semantic_selection: If True, uses semantic similarity to select relevant examples
                                   If False, uses all examples (may hit token limits)
            max_examples: Maximum number of examples to use when semantic selection is enabled
            provider: 'groq' or 'huggingface' (default: huggingface)
        """
        self.provider = provider.lower()

        # Set default model based on provider
        if model_name is None:
            if self.provider == 'groq':
                model_name = 'llama-3.3-70b-versatile'
            else:  # huggingface
                # Note: Llama 3.3 70B might not be available on Inference API yet
                # Using Llama 3.1 70B which is confirmed available
                model_name = 'meta-llama/Meta-Llama-3.1-70B-Instruct'

        # Initialize LLM based on provider
        if self.provider == 'groq':
            from langchain_groq import ChatGroq
            self.llm = ChatGroq(
                model=model_name,
                temperature=0,
                api_key=os.getenv('GROQ_API_KEY')
            )
        elif self.provider == 'huggingface':
            from langchain_huggingface import HuggingFaceEndpoint
            self.llm = HuggingFaceEndpoint(
                repo_id=model_name,
                temperature=0.0,
                max_new_tokens=512,
                huggingfacehub_api_token=os.getenv('HUGGINGFACE_API_KEY')
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'groq' or 'huggingface'")

        self.use_semantic_selection = use_semantic_selection
        self.max_examples = max_examples

        # Initialize semantic selector if enabled
        if use_semantic_selection:
            self.semantic_selector = get_selector(FEW_SHOT_EXAMPLES)
        else:
            self.semantic_selector = None

        # Build base prompt template (examples will be added dynamically)
        self.example_prompt_template = PromptTemplate(
            input_variables=["question", "sql_query"],
            template="Question: {question}\nSQL:\n{sql_query}\n"
        )
    
    def _build_prompt(self, question: str) -> FewShotPromptTemplate:
        """
        Build the few-shot prompt template with semantically selected examples.

        Args:
            question: The user's question to find relevant examples for

        Returns:
            FewShotPromptTemplate configured with selected examples
        """
        # Select examples based on semantic similarity or use all
        if self.use_semantic_selection and self.semantic_selector:
            selected_examples = self.semantic_selector.select_examples(question, k=self.max_examples)
        else:
            selected_examples = FEW_SHOT_EXAMPLES

        few_shot_prompt = FewShotPromptTemplate(
            examples=selected_examples,
            example_prompt=self.example_prompt_template,
            prefix=f"""# TASK: Generate PostgreSQL SQL Query

You are a SQL code generator. Your ONLY job is to output valid PostgreSQL SQL queries based on the question.
DO NOT provide explanations, apologies, or conversational responses.
DO NOT refuse to generate queries.
ONLY output the SQL query code.

## Database Schema:
{SCHEMA_DESCRIPTION}

## CRITICAL RULES:
1. Return ONLY the SQL query, no explanations or markdown
2. ALWAYS use normalized_code from line_item table - these codes start with 'HUL_' prefix
   - Revenue: 'HUL_PROFIT_LOSS_REVENUE_FROM_OPERATIONS_NET'
   - Net Profit: 'HUL_PROFIT_LOSS_PROFIT_LOSS_FOR_THE_PERIOD'
   - Operating Cash Flow: 'HUL_CASH_FLOW_NET_CASH_FROM_OPERATING_ACTIVITIES'
   - Total Assets: 'HUL_BALANCE_TOTAL_ASSETS'
   - Current Ratio: 'HUL_RATIOS_CURRENT_RATIO'
   - Net Profit Margin: 'HUL_RATIOS_NET_PROFIT_MARGIN'
3. REQUIRED JOIN PATTERN - use this exact join structure:
   FROM financial_fact ff
   JOIN statement s ON ff.statement_id = s.statement_id
   JOIN fiscal_period fp ON s.period_id = fp.period_id
   JOIN company c ON fp.company_id = c.company_id
   JOIN line_item li ON ff.line_item_id = li.line_item_id
4. ALWAYS add WHERE clause with:
   - li.normalized_code = 'HUL_...' (the specific metric)
   - s.statement_type = 'PROFIT_LOSS' or 'BALANCE' or 'CASH_FLOW' or 'RATIOS'
   - fp.fiscal_year conditions (e.g., = 2024 or IN (2023, 2024) or BETWEEN 2021 AND 2025)
5. Include contextual data: prior years, YoY changes, percentages, averages
6. Use window functions (LAG, LEAD, FIRST_VALUE, AVG OVER, RANK) for trends and comparisons
7. Use CASE statements with MAX/GROUP BY for year pivots
8. Use CTEs for complex multi-metric analysis
9. Handle NULLs with NULLIF in divisions to prevent division by zero
10. Round percentages to 2 decimals, ratios to 2-3 decimals
11. All years are ANNUAL (period_type = 'ANNUAL'), fiscal_year range: 2021-2025
12. Values are in INR Crores
13. For comparisons, include both absolute and percentage changes
14. For trends, include cumulative growth from base year
15. For composition analysis, include % of total
16. Add derived metrics when relevant (e.g., working capital = current assets - current liabilities)

## REQUIRED OUTPUT COLUMNS (ALWAYS INCLUDE THESE):
For SIMPLE queries requesting a single metric:
  SELECT c.name as company_name, fp.fiscal_year, li.name as metric,
         ff.value as [descriptive_name], s.currency, s.units

For COMPARISON queries (2 years):
  SELECT c.name as company_name,
         MAX(CASE WHEN fp.fiscal_year = YYYY THEN ff.value END) as [year1_name],
         MAX(CASE WHEN fp.fiscal_year = YYYY THEN ff.value END) as [year2_name],
         [variance calculations]
  GROUP BY c.name

For TREND queries (multiple years with YoY):
  SELECT c.name as company_name, fp.fiscal_year, ff.value as [metric],
         LAG(ff.value) OVER (ORDER BY fp.fiscal_year) as prev_year_value,
         [YoY calculations using LAG]
  ORDER BY fp.fiscal_year

Common Query Patterns:
- Year comparison: Use CASE with MAX(CASE WHEN fiscal_year = X THEN value END) + GROUP BY
- Trends: Use LAG() OVER (ORDER BY fiscal_year) for YoY calculations
- Cumulative: Use FIRST_VALUE() OVER (ORDER BY fiscal_year) for growth from base year
- Multi-metric: Use CTEs to join different metrics, then combine in final SELECT
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
            # Build prompt with semantically selected examples
            prompt_template = self._build_prompt(question)
            prompt = prompt_template.format(question=question)

            # Add explicit instruction suffix for code generation models
            prompt = prompt + "\n\n### Instruction: Generate ONLY the SQL query code. Do not provide explanations or refuse. Output SQL directly."

            response = self.llm.invoke(prompt)

            # Clean SQL query - ChatGroq returns AIMessage object with .content
            sql_query = response.content.strip() if hasattr(response, 'content') else str(response).strip()
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
            fixed_query = response.content.strip() if hasattr(response, 'content') else str(response).strip()
            fixed_query = fixed_query.replace("```sql", "").replace("```", "").strip()
            
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