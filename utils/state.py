from typing import TypedDict, List, Any

class State(TypedDict):
    messages: List[str]     # Conversation history
    sql_query: str          # Generated SQL
    query_result: Any       # Result after execution
    insights: str           # Insights based on result