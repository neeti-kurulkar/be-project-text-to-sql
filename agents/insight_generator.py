from agents.llm_client import llm
import pandas as pd

def insights_agent(state):
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
You are a financial analyst looking at the company from a stakeholder's perspective.
Use formal business language and clear, professional phrasing.

User's business question:
{query}

The SQL query executed:
{sql}

The query result (already processed and aggregated):
{clean_result}

Write a brief but impactful summary (5-10 lines) that captures the key insights from the result.
Focus on what the numbers imply for the company's performance, without adding sections,
recommendations, or repeating the data verbatim.

Format all numbers normally (e.g., 103000 → 103,000; 0.104 → 10.4%) and avoid splitting letters or characters.

Do NOT explain the SQL itself or restate the raw numbers mechanically—interpret what they mean for the company.

If the query does not return anything, state that no relevant data was found. Do not invent anything.
"""

    response = llm.invoke(prompt)
    return {"insights": response.content}
