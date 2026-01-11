# Quick Reference Guide

## 🚀 Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Add your API key to `.env`:

```env
AZURE_OPENAI_API_KEY=<your-api-key>
```

### Run

```bash
python main.py          # Interactive mode
python test_agent.py    # Run tests
python example_usage.py # See examples
```

## 💬 Usage

### Interactive Mode

```
You: How many days of annual leave do I get?
Agent: According to the Leave Policy, you are entitled to 20 days of annual leave per year.

You: clear   # Reset conversation
You: quit    # Exit
```

### Programmatic Usage

```python
from main import AIAgent
import os

agent = AIAgent(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# Add documents
agent.add_document(title="Policy", content="...")

# Ask questions
response = agent.process_query("Your question here")
print(response)
```

## 🛠️ Key Features

| Feature             | Description                       |
| ------------------- | --------------------------------- |
| **Direct Answers**  | General knowledge answered by LLM |
| **Document Search** | Policy questions use tool calling |
| **Memory**          | Maintains conversation context    |
| **Smart Routing**   | Automatically decides tool usage  |

## 📝 Commands

- Type any question → Get an answer
- `clear` → Reset conversation history
- `quit` → Exit application

## 🎯 Example Queries

### General (Direct LLM)

- "What is Python?"
- "Explain quantum computing"
- "How does machine learning work?"

### Policy (Uses Tool)

- "How many remote work days?"
- "What's the annual leave policy?"
- "What is the home office stipend?"

### Follow-up (Uses Memory)

- "What about sick leave?" (after asking about annual leave)
- "Can you explain more?" (continues previous topic)

## 📊 Files

```
main.py              → AI Agent implementation
example_usage.py     → Simple usage examples (CURRENT FILE)
test_agent.py        → Automated tests
.env                 → Configuration (API keys)
README.md            → Full documentation
```

## ✅ Requirements Met

✅ Accepts user queries  
✅ Decides: Direct LLM vs Tool  
✅ Returns clear responses  
✅ Uses Azure OpenAI  
✅ Prompt engineering  
✅ Tool calling  
✅ Session memory

## 🔧 Customization

### Add Documents

```python
agent.add_document(
    title="Your Policy",
    content="Policy text..."
)
```

### Add Tools

See `main.py` → `tools` array in `process_query()` method

### Change Model

Update `AZURE_OPENAI_DEPLOYMENT` in `.env`

## 📞 Support

Check `README.md` for full documentation  
Check `IMPLEMENTATION_SUMMARY.md` for technical details  
Run `python test_agent.py` to verify setup

---

**Ready to use!** 🎉
