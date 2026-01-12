"""
Debug the actual prompt being sent to the model
"""
from agents.sql_generator import SQLGeneratorAgent

print("="*80)
print("DEBUGGING PROMPT STRUCTURE")
print("="*80)

agent = SQLGeneratorAgent(model_name='deepseek-coder:6.7b')

question = "What was the revenue in 2024?"
prompt = agent.prompt.format(question=question)

print("\nFull prompt being sent to model:")
print("="*80)
print(prompt)
print("="*80)
print(f"\nPrompt length: {len(prompt)} characters")
print(f"Number of lines: {len(prompt.split(chr(10)))}")
