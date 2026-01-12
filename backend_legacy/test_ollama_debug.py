"""
Debug script to test Ollama with DeepSeek Coder
"""
from agents.sql_generator import SQLGeneratorAgent
import os

print("="*80)
print("DEBUGGING OLLAMA SQL GENERATION")
print("="*80)

# Check environment
print("\n1. Environment Variables:")
print(f"   OLLAMA_MODEL from .env: {os.getenv('OLLAMA_MODEL', 'NOT SET')}")

# Create agent with explicit model
print("\n2. Creating agent with deepseek-coder:6.7b...")
agent = SQLGeneratorAgent(model_name='deepseek-coder:6.7b')
print(f"   Agent LLM type: {type(agent.llm)}")
print(f"   Agent model: {agent.llm.model}")

# Test simple question
print("\n3. Testing SQL generation...")
question = "What was the revenue in 2024?"
print(f"   Question: {question}")

result = agent.generate(question)

print("\n4. Results:")
print(f"   Error: {result.get('error')}")
print(f"   Generated SQL (first 500 chars):")
print("   " + "="*76)
sql = result.get('sql_query', 'NO SQL GENERATED')
print(f"   {sql[:500]}")
print("   " + "="*76)

# Check if it looks like SQL
if sql and any(keyword in sql.upper() for keyword in ['SELECT', 'FROM', 'WHERE', 'JOIN']):
    print("\n✓ Output looks like SQL!")
else:
    print("\n✗ Output does NOT look like SQL - looks conversational")
    print("\n   This usually means:")
    print("   - Model is interpreting prompt as a chat conversation")
    print("   - Need to adjust prompt format for DeepSeek Coder")

print("\n" + "="*80)
