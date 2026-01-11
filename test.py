"""
Simple test script for the AI Support Agent API
Run this after starting the server with: uvicorn api:app --reload
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("=" * 60)
    print("Testing AI Support Agent API")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 2: General question (LLM knowledge)
    print("\n2. Testing general question (LLM knowledge)...")
    response = requests.post(
        f"{BASE_URL}/ask",
        json={
            "query": "What is Python?",
            "session_id": "test_session"
        }
    )
    result = response.json()
    print(f"   Question: What is Python?")
    print(f"   Source: {result['source']}")
    print(f"   Answer: {result['answer'][:100]}...")
    
    # Test 3: Document question (RAG)
    print("\n3. Testing document question (RAG)...")
    response = requests.post(
        f"{BASE_URL}/ask",
        json={
            "query": "How many remote work days are allowed?",
            "session_id": "test_session"
        }
    )
    result = response.json()
    print(f"   Question: How many remote work days are allowed?")
    print(f"   Source: {result['source']}")
    print(f"   Answer: {result['answer'][:150]}...")
    
    # Test 4: Follow-up (uses session memory)
    print("\n4. Testing follow-up question (session memory)...")
    response = requests.post(
        f"{BASE_URL}/ask",
        json={
            "query": "What else can you tell me about that?",
            "session_id": "test_session"
        }
    )
    result = response.json()
    print(f"   Question: What else can you tell me about that?")
    print(f"   Source: {result['source']}")
    print(f"   Answer: {result['answer'][:150]}...")
    
    # Test 5: List sessions
    print("\n5. Testing session list...")
    response = requests.get(f"{BASE_URL}/sessions")
    sessions = response.json()
    print(f"   Active sessions: {sessions['active_sessions']}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Please start the server first with: uvicorn api:app --reload")
    except Exception as e:
        print(f"Error: {e}")
