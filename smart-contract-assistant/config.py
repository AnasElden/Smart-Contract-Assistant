"""
Simple configuration for Smart Contract Assistant
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Directories
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
VECTOR_STORE_DIR = BASE_DIR / "vector_stores"

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)
VECTOR_STORE_DIR.mkdir(exist_ok=True)

# LLM Settings
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # ollama, huggingface, nvidia
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Vector Store
VECTOR_STORE_NAME = "contract_store"
VECTOR_STORE_TYPE = "chroma"  # chroma or faiss

# Chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval
TOP_K = 5

# API
API_PORT = 8001
UI_PORT = 7864  # Changed to avoid port conflicts
