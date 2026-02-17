# 📄 Smart Contract Q&A Assistant

AI-powered document analysis tool. Upload contracts, ask questions, get instant answers with citations - 100% local and private.

## ✨ Features

- 🤖 Natural language Q&A on documents
- 📚 Source citations for every answer
- 🔒 100% private - all processing local
- 📄 Supports PDF and DOCX files
- ⚡ Fast setup (5 minutes)
- 💾 No API costs - uses free local LLM

## 🚀 Quick Start

### Prerequisites

```bash
# 1. Install Ollama (free local LLM)
# Download from: https://ollama.ai

# 2. Pull the model
ollama pull llama3.2
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

**Open http://localhost:7864 in your browser!**

## 📖 How to Use

### 1. Upload Document
- Click **"📤 Upload Document"** tab
- Select PDF or DOCX file
- Wait for processing (~10 seconds)

### 2. Ask Questions
- Switch to **"💬 Chat"** tab
- Type your question
- Get instant answers with citations

### 3. Get Summary (Optional)
- Click **"📄 Summarize"** button

**Example Questions:**
- "What are the payment terms?"
- "Who are the parties involved?"
- "What is the termination clause?"

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Gradio    │────▶│   FastAPI    │────▶│   Ollama    │
│     UI      │     │   Backend    │     │  (LLM)      │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  ChromaDB    │
                    │ Vector Store │
                    └──────────────┘
```

**Tech Stack:**
- LangChain - RAG pipeline
- Ollama - Local LLM (free)
- ChromaDB - Vector database
- FastAPI - API backend
- Gradio - Web interface

## 📁 Project Structure

```
smart-contract-assistant/
├── main.py                 # Entry point - run this
├── api_server.py          # FastAPI backend
├── gradio_ui.py           # Web interface
├── rag_chain.py           # RAG pipeline logic
├── document_processor.py  # PDF/DOCX parsing
├── vector_store.py        # Embedding management
├── guardrails.py          # Answer validation
├── config.py              # Configuration
└── requirements.txt       # Dependencies
```

## ⚙️ Configuration

Edit `config.py`:

```python
LLM_MODEL = "llama3.2"        # Change model
CHUNK_SIZE = 1000             # Text chunk size
CHUNK_OVERLAP = 200           # Overlap
TOP_K = 5                     # Retrieved chunks
API_PORT = 8001               # Backend port
UI_PORT = 7864                # Frontend port
```

## 🔌 API Endpoints (Optional)

```bash
# Health check
GET http://localhost:8001/health

# Upload document
POST http://localhost:8001/upload

# Ask question
POST http://localhost:8001/qa?question=YOUR_QUESTION

# Get summary
POST http://localhost:8001/summarize
```

Interactive docs: **http://localhost:8001/docs** (when running)

## 🛠️ Advanced Usage

### Run Components Separately

```bash
# Terminal 1: Start API
python api_server.py

# Terminal 2: Start UI
python gradio_ui.py
```

### API-Only Mode

```bash
python main.py --mode api
```

### UI-Only Mode

```bash
python main.py --mode ui
```

### Use Different Model

```python
# In config.py
LLM_MODEL = "mistral"  # or phi3, gemma, etc.
```

Then pull the model:
```bash
ollama pull mistral
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Ollama not found" | Install from [ollama.ai](https://ollama.ai) and run `ollama pull llama3.2` |
| "Port in use" | Change `API_PORT` or `UI_PORT` in config.py |
| Slow responses | Normal for local AI (3-8 sec), try smaller model |
| No answers | Verify Ollama is running: `ollama serve` |
| Module errors | Run `pip install -r requirements.txt` |

## 📊 Performance

- **Upload Time:** 5-10 seconds (avg 10-page PDF)
- **Query Response:** 3-8 seconds
- **Accuracy:** Grounded in source documents only
- **Privacy:** 100% local - no external API calls

## 🎓 What This Demonstrates

- ✅ RAG (Retrieval Augmented Generation) pipeline
- ✅ Vector database integration
- ✅ LLM orchestration with LangChain
- ✅ Microservices architecture (FastAPI)
- ✅ Document processing strategies
- ✅ Answer validation and guardrails

## 📄 License

MIT License - see LICENSE file

## 🙏 Built With

- [LangChain](https://www.langchain.com/)
- [Ollama](https://ollama.ai/)
- [ChromaDB](https://www.trychroma.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Gradio](https://www.gradio.app/)

---

**Built for NVIDIA DLI Workshop on LLM Pipelines**
