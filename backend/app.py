import streamlit as st
import re
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from utils.state import State
from agents.text_to_sql import text_to_sql_agent
from agents.query_executor import query_executor_agent
from agents.insight_generator import insights_agent
from agents.summary_agent import company_summary_agent

load_dotenv()  # Load DB credentials

DB_PARAMS = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD")
}

def query_db(query):
    """Run a query on PostgreSQL and return as DataFrame."""
    conn = psycopg2.connect(**DB_PARAMS)
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df

# ---------------- Streamlit Page Setup ----------------
st.set_page_config(page_title="Financial Insights Dashboard", layout="wide", page_icon="💹")

graph = StateGraph(State)
graph.add_node("text_to_sql", text_to_sql_agent)
graph.add_node("query_executor", query_executor_agent)
graph.add_node("insights", insights_agent)
graph.set_entry_point("text_to_sql")
graph.add_edge("text_to_sql", "query_executor")
graph.add_edge("query_executor", "insights")
graph.add_edge("insights", END)
app = graph.compile()

# Sidebar navigation
st.sidebar.title("Financial Insights")
page = st.sidebar.radio("Navigate to", ["Ask a Question", "View Data"], index=0)

# Sidebar: Example questions
with st.sidebar.expander("💡 Example Questions"):
    st.markdown("""
    - How far are we from meeting planned operating profit in Q4 2023?  
    - How did net income change across quarters in 2023?  
    - What was the total revenue in 2023?  
    - How did total assets change year-over-year?  
    - How did total liabilities change year-over-year?  
    - Compare cash and accounts receivable vs. accounts payable at the end of 2023
    """)

# ---------------- Ask a Question Page ----------------
if page == "Ask a Question":
    st.title("💬 Ask a Financial Question")

    # Company summary
    summary_state = {}
    summary_output = company_summary_agent(summary_state)
    st.subheader("🏢 Company Overview")
    st.info(summary_output.get("summary", "Summary not available."))

    # Chat interface
    user_query = st.text_input("Enter your question here", value="How did net income change across quarters in 2023?")
    if st.button("Submit") and user_query:
        with st.spinner("Generating SQL and Insights..."):
            output = app.invoke({"messages": [user_query]})

        # Tabs for display
        tabs = st.tabs(["Insights", "Generated SQL Query", "Query Result"])

        # SQL Query
        with tabs[1]:
            st.subheader("SQL Query Generated")
            st.code(output.get("sql_query", "N/A"))

        # Query Result
        with tabs[2]:
            st.subheader("Query Result")
            result = output.get("query_result", None)
            if isinstance(result, list) and result:
                df = pd.DataFrame(result)
                df.fillna(0, inplace=True)
                st.dataframe(df)
            elif isinstance(result, pd.DataFrame):
                df = result.fillna(0)
                st.dataframe(df)
            else:
                st.write(result if result else "No data returned.")

        # Insights
        with tabs[0]:
            st.subheader("Insights")
            
            insights_text = output.get("insights", "No insights generated.")

            # Remove unwanted newlines and excessive spaces
            insights_text = re.sub(r'\n+', ' ', insights_text)          # replace all line breaks with a space
            insights_text = re.sub(r'\s+', ' ', insights_text)          # collapse multiple spaces
            insights_text = insights_text.strip()                        # remove leading/trailing spaces

            st.success(insights_text)


# ---------------- View Data Page ----------------
elif page == "View Data":
    st.title("📊 View Financial Data")

    table_name = st.selectbox("Select table", 
                              ["company", "fiscal_period", "statement", "line_item", "financial_fact"])
    if table_name:
        df = query_db(f"SELECT * FROM {table_name}")
        df.fillna(0, inplace=True)
        st.dataframe(df)