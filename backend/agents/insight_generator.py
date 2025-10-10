from agents.llm_client import llm
import pandas as pd

def insights_agent(state):
    """
    Generates natural language insights from a SQL query result.

    Expects the state dictionary to contain:
    - "query_result": the output of the SQL query (DataFrame, list of dicts, or None)
    - "user_query": the original user question
    - "sql_query": the SQL that produced the results
    """
    result = state.get("query_result", None)
    query = state.get("user_query", "")
    sql = state.get("sql_query", "")

    # ---------------- Preprocess the result ----------------
    def preprocess_result(result):
        if isinstance(result, pd.DataFrame):
            return result.to_string(index=False)
        elif isinstance(result, list):
            if result:
                return pd.DataFrame(result).to_string(index=False)
            return "No relevant data found."
        return str(result) if result else "No relevant data found."

    clean_result = preprocess_result(result)

    # ---------------- Build prompt ----------------
    prompt = f"""
You are a professional financial analyst reviewing company performance data.
Your goal is to provide clear, concise insights for stakeholders based on the query result.

User's business question:
{query}

The SQL query executed:
{sql}

The query result (already processed and aggregated):
{clean_result}

Instructions:
1. Summarize the key findings in 5-10 lines in formal business language.
2. All numbers are in Indian Rupees (INR) crores, as returned by the query.
3. Use commas for readability (e.g., 79880 → 79,880).
4. Do NOT convert to other currencies or invent numbers.
5. Interpret what the numbers imply for the company's performance.
6. If the query result is blank, or an error, do not give any insights, just mention that an error occured.
7. Do NOT provide recommendations.
8. DO NOT INVENT ANYTHING.

"""

    response = llm.invoke(prompt)
    return {"insights": response.content.strip()}