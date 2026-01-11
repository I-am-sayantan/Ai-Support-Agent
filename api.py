"""
AI Support Agent - FastAPI Backend with RAG
Simple, self-contained API server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from openai import AzureOpenAI
from rag_system import RAGSystem

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="AI Support Agent API",
    description="RAG-powered AI support agent",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage
sessions: Dict[str, Dict] = {}

# RAG System (singleton)
rag_system = None


def get_rag_system() -> RAGSystem:
    """Get or create RAG system instance"""
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            embedding_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        )
        # Load existing index
        if os.path.exists("rag_index"):
            rag_system.load_index("rag_index")
    return rag_system


class RAGAgent:
    """AI Agent with RAG capabilities"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.conversation_history = []
        self.rag_system = get_rag_system()
        
        # Define tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_documents",
                    "description": "Search company documents for specific information about policies, procedures, products, or technical details",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    
    def search_documents(self, query: str) -> str:
        """Search documents using RAG"""
        results = self.rag_system.search(query, top_k=3)
        
        if not results:
            return "No relevant documents found."
        
        # Format results
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"{i}. [Source: {result['metadata']['source']}]\n{result['chunk'][:300]}..."
            )
        
        return "\n\n".join(formatted)
    
    def process_query(self, query: str) -> str:
        """Process a user query with RAG support"""
        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": query
        })
        
        # Get AI response
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Use the search_documents tool when users ask about company policies, procedures, products, or technical information. For general questions, answer directly."
                },
                *self.conversation_history
            ],
            tools=self.tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        # Handle tool calls
        if message.tool_calls:
            # Add assistant message with tool call
            self.conversation_history.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })
            
            # Execute tool
            for tool_call in message.tool_calls:
                if tool_call.function.name == "search_documents":
                    import json
                    args = json.loads(tool_call.function.arguments)
                    result = self.search_documents(args["query"])
                    
                    # Add tool response
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "search_documents",
                        "content": result
                    })
            
            # Get final response
            final_response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Use the search_documents tool when users ask about company policies, procedures, products, or technical information. For general questions, answer directly."
                    },
                    *self.conversation_history
                ]
            )
            
            final_message = final_response.choices[0].message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": final_message
            })
            
            return final_message
        else:
            # Direct answer
            self.conversation_history.append({
                "role": "assistant",
                "content": message.content
            })
            return message.content


# Request/Response Models
class AskRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    source: str
    session_id: str


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Support Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check"""
    index_exists = os.path.exists("rag_index/index.faiss")
    return {
        "status": "healthy" if index_exists else "warning",
        "rag_index": "loaded" if index_exists else "not found",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """Ask a question"""
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        
        if session_id not in sessions:
            sessions[session_id] = {
                "agent": RAGAgent(),
                "created_at": datetime.now().isoformat()
            }
        
        # Process query
        agent = sessions[session_id]["agent"]
        answer = agent.process_query(request.query)
        
        # Determine source
        source = "llm"
        for msg in agent.conversation_history:
            if msg.get("role") == "tool":
                source = "documents"
                break
        
        return {
            "answer": answer,
            "source": source,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
async def list_sessions():
    """List active sessions"""
    return {
        "active_sessions": len(sessions),
        "sessions": list(sessions.keys())
    }


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session deleted"}
    raise HTTPException(status_code=404, detail="Session not found")


@app.post("/rebuild-index")
async def rebuild_index():
    """Rebuild RAG index"""
    try:
        global rag_system
        rag_system = RAGSystem(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            embedding_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        )
        
        # Build index
        documents = {}
        docs_dir = "documents"
        for filename in os.listdir(docs_dir):
            if filename.endswith('.txt'):
                with open(os.path.join(docs_dir, filename), 'r', encoding='utf-8') as f:
                    documents[filename] = f.read()
        
        rag_system.build_index(documents)
        rag_system.save_index("rag_index")
        
        return {"message": "Index rebuilt successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
