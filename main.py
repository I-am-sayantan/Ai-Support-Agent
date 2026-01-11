import os
from typing import List, Dict, Optional
from openai import AzureOpenAI
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIAgent:
    def __init__(self, api_key: str, azure_endpoint: str, deployment_name: str, api_version: str = "2024-12-01-preview"):
        """Initialize the AI agent with Azure OpenAI credentials."""
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )
        self.deployment_name = deployment_name
        self.conversation_history: List[Dict] = []
        self.documents: List[Dict] = []
        
    def add_document(self, title: str, content: str):
        """Add a document to the agent's knowledge base."""
        self.documents.append({
            "title": title,
            "content": content
        })
    
    def search_documents(self, query: str) -> str:
        """Tool: Search through documents for relevant information."""
        if not self.documents:
            return "No documents available."
        
        # Simple search - finds documents containing query keywords
        relevant_docs = []
        query_lower = query.lower()
        
        for doc in self.documents:
            if any(word in doc["content"].lower() for word in query_lower.split()):
                relevant_docs.append(f"**{doc['title']}**\n{doc['content']}")
        
        if relevant_docs:
            return "\n\n---\n\n".join(relevant_docs)
        return "No relevant documents found."
    
    def process_query(self, user_query: str) -> str:
        """Process user query and decide whether to use documents or answer directly."""
        
        # Define available tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_documents",
                    "description": "Search through company documents for specific information about policies, procedures, or guidelines",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to find relevant document content"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_query
        })
        
        # System message with instructions
        messages = [
            {
                "role": "system",
                "content": """You are a helpful AI assistant. You can answer questions directly using your knowledge, 
                or search through provided company documents when the question is about specific policies or internal information.
                
                When answering:
                - Be clear and concise
                - If you use document information, cite the source
                - If you're unsure, say so
                """
            }
        ] + self.conversation_history
        
        # First API call - let the model decide if it needs tools
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # If the model wants to use a tool
        if tool_calls:
            # Add assistant's tool call to history
            self.conversation_history.append(response_message)
            
            # Execute tool calls
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "search_documents":
                    function_response = self.search_documents(
                        query=function_args.get("query")
                    )
                    
                    # Add tool response to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_response
                    })
            
            # Second API call - get final response with tool results
            second_response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful AI assistant. You can answer questions directly using your knowledge, 
                        or search through provided company documents when the question is about specific policies or internal information.
                        
                        When answering:
                        - Be clear and concise
                        - If you use document information, cite the source
                        - If you're unsure, say so
                        """
                    }
                ] + self.conversation_history
            )
            
            final_response = second_response.choices[0].message.content
        else:
            # No tool needed, use direct response
            final_response = response_message.content
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })
        
        return final_response
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


def main():
    # Configuration - Update with your Azure OpenAI credentials
    API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "<your-api-key>")
    AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://sayan-mka1tkzo-eastus2.cognitiveservices.azure.com/")
    DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT", "sayantan-chat")
    API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    
    # Initialize agent
    agent = AIAgent(
        api_key=API_KEY,
        azure_endpoint=AZURE_ENDPOINT,
        deployment_name=DEPLOYMENT_NAME,
        api_version=API_VERSION
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
    
    # Interactive loop
    print("AI Agent Ready! Type 'quit' to exit, 'clear' to reset conversation.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            break
        
        if user_input.lower() == 'clear':
            agent.clear_history()
            print("Conversation history cleared.\n")
            continue
        
        if not user_input:
            continue
        
        try:
            response = agent.process_query(user_input)
            print(f"\nAgent: {response}\n")
        except Exception as e:
            print(f"Error: {str(e)}\n")


if __name__ == "__main__":
    main()