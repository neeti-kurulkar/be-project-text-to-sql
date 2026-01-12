"""
Test full SQL generation and execution pipeline
"""
from agents.sql_generator import SQLGeneratorAgent
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("="*80)
print("TESTING FULL SQL GENERATION PIPELINE")
print("="*80)

# Create agent
print("\n1. Creating SQL Generator Agent...")
agent = SQLGeneratorAgent(model_name='deepseek-coder:6.7b')
print("   ✓ Agent created")

# Test question
question = "What was the revenue in 2024?"
print(f"\n2. Question: {question}")

# Generate SQL
print("\n3. Generating SQL...")
result = agent.generate(question)

if result.get('error'):
    print(f"   ✗ Error: {result['error']}")
    exit(1)

sql_query = result['sql_query']
print(f"   ✓ SQL Generated:")
print(f"\n{sql_query}\n")

# Try to execute
print("4. Attempting to execute query...")
try:
    conn = psycopg2.connect(
        host=os.getenv('PGHOST'),
        port=os.getenv('PGPORT'),
        database=os.getenv('PGDATABASE'),
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD')
    )
    cursor = conn.cursor()

    cursor.execute(sql_query)
    results = cursor.fetchall()

    print(f"   ✓ Query executed successfully!")
    print(f"   ✓ Returned {len(results)} rows")

    if results:
        print("\n5. Sample Results (first 3 rows):")
        for i, row in enumerate(results[:3], 1):
            print(f"   Row {i}: {row}")

    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("✓ PIPELINE TEST SUCCESSFUL!")
    print("="*80)

except Exception as e:
    print(f"   ✗ Execution Error: {str(e)}")
    print("\n   Note: The SQL was generated, but may need adjustment.")
    print("   This is expected for first attempts - the few-shot examples will help.")
    print("\n" + "="*80)
