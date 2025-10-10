from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",  # lightweight & fast
    api_key=os.getenv("GROQ_API_KEY"),
)