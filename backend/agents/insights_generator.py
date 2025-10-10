"""
Insights Generator Agent
Generates structured business insights from SQL query results
"""

import os
import pandas as pd
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()


class InsightsGeneratorAgent:
    def __init__(self):
        """Initialize the Insights Generator Agent."""
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,  # Slightly higher for more natural language
            api_key=os.getenv('GROQ_API_KEY')
        )
    
    def _format_dataframe(self, df: pd.DataFrame) -> str:
        """Format DataFrame for LLM consumption."""
        # Limit to first 50 rows for context window
        df_limited = df.head(50)
        
        # Convert to readable string format
        return df_limited.to_string(index=False)
    
    def generate(self, question: str, sql_query: str, results: pd.DataFrame) -> dict:
        """
        Generate business insights from query results.
        
        Args:
            question: Original user question
            sql_query: SQL query that was executed
            results: Query results as DataFrame
            
        Returns:
            Dictionary with 'insights', 'summary', and 'error' keys
        """
        try:
            # Format results
            formatted_results = self._format_dataframe(results)
            
            # Build prompt
            prompt = f"""You are a financial analyst generating insights from HUL's financial data.

USER QUESTION:
{question}

SQL QUERY EXECUTED:
{sql_query}

QUERY RESULTS:
{formatted_results}

CONTEXT:
- Company: Hindustan Unilever Limited (HUL)
- Industry: FMCG
- Currency: INR Crores
- Time Period: 2021-2025 (Annual Data)

Generate structured business insights following this format:

## Executive Summary
[1-2 sentence high-level takeaway answering the user's question directly]

## Key Findings
[3-5 bullet points with the most important insights. Each bullet should be specific with numbers]

## Analysis
[2-3 short paragraphs providing deeper analysis, trends, and context]

## Implications
[2-3 bullet points on what this means for business strategy or performance]

GUIDELINES:
1. Be concise and business-focused
2. Always include specific numbers and percentages from the data
3. Highlight trends (improving/declining) and magnitude of changes
4. Compare periods when relevant (YoY, vs average, etc.)
5. Use clear business language, avoid technical jargon
6. If data shows concerning trends, mention them objectively
7. Keep total length under 400 words
8. Use professional tone appropriate for executive reporting
9. Format with markdown headers and bullet points

Generate the insights:"""
            
            # Get insights from LLM
            response = self.llm.invoke(prompt)
            insights = response.content.strip()
            
            # Extract executive summary (first paragraph)
            summary_end = insights.find("\n\n")
            if summary_end > 0:
                # Skip the "## Executive Summary" header
                summary_start = insights.find("\n", insights.find("## Executive Summary")) + 1
                summary = insights[summary_start:summary_end].strip()
            else:
                summary = "Analysis completed. See full insights for details."
            
            return {
                "insights": insights,
                "summary": summary,
                "error": None
            }
            
        except Exception as e:
            return {
                "insights": None,
                "summary": None,
                "error": f"Insights Generation Error: {str(e)}"
            }
    
    def generate_comparison_insights(self, 
                                     question: str, 
                                     results: pd.DataFrame,
                                     comparison_type: str = "temporal") -> dict:
        """
        Generate insights specifically for comparison queries.
        
        Args:
            question: Original question
            results: Query results
            comparison_type: Type of comparison ('temporal', 'metric', 'composition')
            
        Returns:
            Dictionary with insights
        """
        try:
            formatted_results = self._format_dataframe(results)
            
            prompt = f"""Generate concise comparison insights for HUL financial data.

QUESTION: {question}
COMPARISON TYPE: {comparison_type}

DATA:
{formatted_results}

Provide:
1. Main finding (1 sentence)
2. Key differences (2-3 bullets with numbers)
3. Trend assessment (improving/declining/stable)
4. One actionable implication

Keep under 150 words total. Be specific and data-driven."""
            
            response = self.llm.invoke(prompt)
            insights = response.content.strip()
            
            return {
                "insights": insights,
                "summary": insights.split('\n')[0],
                "error": None
            }
            
        except Exception as e:
            return {
                "insights": None,
                "summary": None,
                "error": f"Comparison Insights Error: {str(e)}"
            }
    
    def generate_trend_insights(self, 
                               question: str, 
                               results: pd.DataFrame) -> dict:
        """
        Generate insights specifically for trend analysis.
        
        Args:
            question: Original question
            results: Query results with time-series data
            
        Returns:
            Dictionary with insights
        """
        try:
            formatted_results = self._format_dataframe(results)
            
            prompt = f"""Analyze the trend in HUL's financial data.

QUESTION: {question}

TIME-SERIES DATA:
{formatted_results}

Provide:
1. Overall trend direction (1 sentence)
2. Growth rate or change magnitude
3. Notable inflection points or anomalies (if any)
4. 3-year outlook based on trend
5. Risk or opportunity identified

Keep under 200 words. Focus on actionable insights."""
            
            response = self.llm.invoke(prompt)
            insights = response.content.strip()
            
            return {
                "insights": insights,
                "summary": insights.split('\n')[0],
                "error": None
            }
            
        except Exception as e:
            return {
                "insights": None,
                "summary": None,
                "error": f"Trend Insights Error: {str(e)}"
            }


if __name__ == "__main__":
    # Test the agent
    agent = InsightsGeneratorAgent()
    
    # Sample data
    test_data = pd.DataFrame({
        'fiscal_year': [2021, 2022, 2023, 2024, 2025],
        'revenue': [48326, 51468, 54884, 59414, 62849],
        'yoy_growth_pct': [None, 6.5, 6.64, 8.25, 5.78]
    })
    
    test_question = "What is the revenue trend over the years?"
    test_sql = "SELECT fiscal_year, revenue, yoy_growth_pct FROM revenue_analysis"
    
    print("Generating insights...")
    result = agent.generate(test_question, test_sql, test_data)
    
    if result["error"]:
        print(f"Error: {result['error']}")
    else:
        print("\n" + "="*80)
        print("INSIGHTS")
        print("="*80)
        print(result["insights"])
        print("\n" + "="*80)
        print("SUMMARY:", result["summary"])