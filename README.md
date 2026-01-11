# AI Support Agent

AI Support Agent with Azure OpenAI & Tool Calling

## ✨ Features

✅ **Direct LLM Responses**: Answers general questions using Azure OpenAI (gpt-4o-mini)  
✅ **Document Search Tool**: Searches through provided documents for specific information  
✅ **Session-based Memory**: Maintains conversation context during the session  
✅ **Tool Calling**: Automatically decides when to use document search  
✅ **Prompt Engineering**: Optimized system prompts for better responses

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `.env` file with your Azure OpenAI credentials:

```env
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_ENDPOINT=https://sayan-mka1tkzo-eastus2.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=sayantan-chat
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### 3. Run the Agent

```bash
python main.py
```

### 4. Test the Agent

```bash
python test_agent.py
```

## 💡 Usage Examples

### General Knowledge Query (Direct LLM)

```
You: What is Python?
Agent: Python is a high-level, interpreted programming language...
```

### Policy Question (Uses Document Search Tool)

```
You: How many days of annual leave do I get?
Agent: According to the Leave Policy, you are entitled to 20 days of annual leave per year.
```

### Follow-up Questions (Uses Memory)

```
You: What about sick leave?
Agent: You get 10 days of sick leave per year...
```

## 🏗️ Architecture

### How It Works

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│     Azure OpenAI + Tool Calling     │
│  (Decides: Direct Answer vs Tool)   │
└─────────────┬───────────────────────┘
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
┌─────────────┐  ┌────────────────┐
│   Direct    │  │ Document Search│
│   Answer    │  │     Tool       │
└─────────────┘  └────────┬───────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Final Response  │
                 │  with Context   │
                 └─────────────────┘
```

### Core Components

1. **AIAgent Class**

   - Orchestrates conversation flow
   - Manages tool calling decisions
   - Maintains conversation history

2. **Tool System**

   - `search_documents()`: Keyword-based document search
   - Automatically invoked for policy queries
   - Returns relevant document excerpts

3. **Memory System**

   - Session-based conversation history
   - Maintains context across queries
   - Clearable with 'clear' command

4. **Document Store**
   - In-memory storage
   - Simple keyword matching
   - Extensible architecture

## 🛠️ Extending the Agent

### Add New Tools

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_tax",
            "description": "Calculate tax based on salary",
            "parameters": {
                "type": "object",
                "properties": {
                    "salary": {"type": "number", "description": "Annual salary"}
                },
                "required": ["salary"]
            }
        }
    }
]
```

### Add More Documents

```python
agent.add_document(
    title="IT Security Policy",
    content="All employees must use 2FA..."
)
```

## 📋 Available Commands

- Type any question to get an answer
- `clear` - Reset conversation history
- `quit` - Exit the application

## 🔧 Technical Stack

- **Language**: Python 3.8+
- **LLM**: Azure OpenAI (gpt-4o-mini)
- **API Version**: 2024-12-01-preview
- **Libraries**: openai, python-dotenv
- **Features**: Function Calling, Chat Completions

## 📝 Requirements Met

✅ Accepts user queries  
✅ Decides between direct LLM response or document search  
✅ Uses Azure OpenAI API  
✅ Implements prompt engineering  
✅ Implements tool calling (search_documents)  
✅ Maintains session-based memory  
✅ Returns clear, structured responses

## 🎯 Example Use Case

**Scenario**: Company internal policy assistant

The agent can answer:

- General questions using its LLM knowledge
- Company-specific policy questions using document search
- Follow-up questions using conversation memory

Perfect for HR departments, employee onboarding, or internal support teams!
