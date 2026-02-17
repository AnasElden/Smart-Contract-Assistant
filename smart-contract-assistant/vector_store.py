"""
Simple vector store manager using Chroma
"""
import logging
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
# BaseRetriever is not needed for this simple version

from config import EMBEDDING_MODEL, VECTOR_STORE_DIR, VECTOR_STORE_NAME

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Manage vector store for document embeddings"""
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.vector_store: Optional[Chroma] = None
        self.persist_directory = VECTOR_STORE_DIR / VECTOR_STORE_NAME
    
    def create_vector_store(self, documents: List[Document], store_name: str = None):
        """Create a new vector store from documents"""
        logger.info(f"Creating vector store with {len(documents)} documents")
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=str(self.persist_directory)
        )
        logger.info("Vector store created successfully")
    
    def add_documents(self, documents: List[Document]):
        """Add documents to existing vector store"""
        if self.vector_store is None:
            raise ValueError("Vector store not initialized")
        self.vector_store.add_documents(documents)
        logger.info(f"Added {len(documents)} documents to vector store")
    
    def load_vector_store(self):
        """Load existing vector store"""
        if not self.persist_directory.exists():
            logger.warning(f"Vector store not found at {self.persist_directory}")
            return False
        
        try:
            self.vector_store = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings
            )
            logger.info("Vector store loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def get_retriever(self, k: int = 5):
        """Get a retriever from the vector store"""
        if self.vector_store is None:
            raise ValueError("Vector store not initialized")
        return self.vector_store.as_retriever(search_kwargs={"k": k})
