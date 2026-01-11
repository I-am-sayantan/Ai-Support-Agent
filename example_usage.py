"""
Simple example demonstrating how to use the AI Agent programmatically
"""
import os
from dotenv import load_dotenv
from main import AIAgent

# Load environment variables
load_dotenv()

# Initialize the agent
agent = AIAgent(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# Add your company documents
agent.add_document(
    title="Remote Work Policy",
    content="""Our company supports remote work with the following guidelines:
    - Employees can work remotely up to 3 days per week
    - Core hours are 10 AM - 3 PM in your local timezone
    - You must be available on Slack during core hours
    - Monthly in-person meetings are required
    - Home office equipment stipend: $500 annually"""
)

agent.add_document(
    title="Leave Policy",
    content="""Leave entitlements:
    - Annual Leave: 20 days per year
    - Sick Leave: 10 days per year
    - Parental Leave: 16 weeks paid
    - Leave requests must be submitted 2 weeks in advance
    - Manager approval required for leaves over 3 consecutive days"""
)

# Example 1: General knowledge question
print("Example 1: General Knowledge")
print("-" * 50)
response = agent.process_query("What is artificial intelligence?")
print(f"Q: What is artificial intelligence?")
print(f"A: {response}\n")

# Example 2: Policy-specific question (will use document search)
print("\nExample 2: Policy Question (Uses Tool)")
print("-" * 50)
response = agent.process_query("How many remote work days am I allowed?")
print(f"Q: How many remote work days am I allowed?")
print(f"A: {response}\n")

# Example 3: Follow-up question (uses memory)
print("\nExample 3: Follow-up Question (Uses Memory)")
print("-" * 50)
response = agent.process_query("What about the home office stipend?")
print(f"Q: What about the home office stipend?")
print(f"A: {response}\n")

# Example 4: Clear conversation and start fresh
print("\nExample 4: Clearing Memory and Starting Fresh")
print("-" * 50)
agent.clear_history()
response = agent.process_query("What are the sick leave days?")
print(f"Q: What are the sick leave days?")
print(f"A: {response}\n")

print("\n" + "="*50)
print("All examples completed successfully!")
print("="*50)
