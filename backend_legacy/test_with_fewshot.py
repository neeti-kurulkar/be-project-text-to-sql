"""
Test SQL generation with few-shot examples
"""
from agents.sql_generator import SQLGeneratorAgent
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("="*80)
print("TESTING FEW-SHOT SQL GENERATION")
print("="*80)

# Create agent with DeepSeek Coder
agent = SQLGeneratorAgent(model_name='deepseek-coder:6.7b')

# Test questions that should use the patterns from few-shot examples
test_questions = [
    "What was the total revenue in 2024?",
    "What is the revenue variance between 2023 and 2024?",
    "Show me net profit margin for 2024"
]

# Database connection
conn = psycopg2.connect(
    host=os.getenv('PGHOST'),
    port=os.getenv('PGPORT'),
    database=os.getenv('PGDATABASE'),
    user=os.getenv('PGUSER'),
    password=os.getenv('PGPASSWORD')
)

for i, question in enumerate(test_questions, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}: {question}")
    print('='*80)

    # Generate SQL
    result = agent.generate(question)
    sql = result['sql_query']

    print(f"\nGenerated SQL:")
    print(sql)

    # Try to execute
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()

        print(f"\n✓ Execution: SUCCESS")
        print(f"✓ Rows returned: {len(results)}")

        if results:
            print("\nSample result:")
            print(f"  {results[0]}")
        else:
            print("\n⚠ No results (query executed but returned 0 rows)")
            print("  This might mean the normalized_code is still incorrect.")

        cursor.close()

    except Exception as e:
        print(f"\n✗ Execution: FAILED")
        print(f"  Error: {str(e)[:200]}")

conn.close()

print("\n" + "="*80)
print("FEW-SHOT TEST COMPLETE")
print("="*80)
print("\nNOTE: If queries execute but return 0 rows, the model may need more")
print("      context or the few-shot examples need adjustment.")
print("      The important thing is NO SYNTAX ERRORS = SQL is valid!")
