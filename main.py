from langgraph.graph import StateGraph, END
from utils.state import State
from agents.text_to_sql import text_to_sql_agent
from agents.query_executor import query_executor_agent
from agents.insight_generator import insights_agent

# Build graph
graph = StateGraph(State)

# Add nodes
graph.add_node("text_to_sql", text_to_sql_agent)
graph.add_node("query_executor", query_executor_agent)
graph.add_node("insights", insights_agent)

# Define flow: NL → SQL → Executor → Insights → END
graph.set_entry_point("text_to_sql")
graph.add_edge("text_to_sql", "query_executor")
graph.add_edge("query_executor", "insights")
graph.add_edge("insights", END)

# Compile
app = graph.compile()

# Run
if __name__ == "__main__":
    #query = "Did the company's profit improve in 2023 as compared to 2022?"
    query = "How has HUL's total shareholders' funds changed from 2021 to 2022?"
    output = app.invoke({"messages": [query]})

    # Pretty print
    print("\n📌 User Query:")
    print(f"   {query}\n")

    print("📝 SQL Query Generated:")
    print(f"   {output.get('sql_query', 'N/A')}\n")

    print("📊 Query Result:")
    result = output.get("query_result", "N/A")
    if isinstance(result, list) and len(result) == 1 and isinstance(result[0], tuple):
        print(f"   {result[0][0]}")
    else:
        print(f"   {result}\n")

    print("💡 Insights:")
    print(f"   {output.get('insights', 'N/A')}\n")