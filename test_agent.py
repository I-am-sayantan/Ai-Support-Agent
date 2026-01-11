"""
Test script to demonstrate the AI Agent capabilities
"""
import os
from openai import AzureOpenAI
import json
from dotenv import load_dotenv
from main import AIAgent

# Load environment variables
load_dotenv()

def test_agent():
    """Test the AI agent with various queries"""
    
    # Initialize agent
    agent = AIAgent(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
    
    # Add sample documents
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
    
    # Test queries
    test_queries = [
        "What is Python?",  # General knowledge - should answer directly
        "How many days of remote work are allowed?",  # Policy question - should use document search
        "What is the home office stipend?",  # Specific policy detail
        "Explain quantum computing in simple terms"  # General knowledge
    ]
    
    print("=" * 80)
    print("AI AGENT TEST DEMONSTRATION")
    print("=" * 80)
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {query}")
        print('='*80)
        
        try:
            response = agent.process_query(query)
            print(f"\n✓ Response:\n{response}")
            print()
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            print()
        
        # Add a separator between tests
        if i < len(test_queries):
            print("\n" + "-"*80 + "\n")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_agent()
