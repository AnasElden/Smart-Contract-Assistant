"""
RAG chain for question answering with document retrieval
"""
import logging
from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from config import LLM_PROVIDER, LLM_MODEL

logger = logging.getLogger(__name__)

class RAGChain:
    """RAG chain for question answering"""
    
    def __init__(self, retriever):
        self.retriever = retriever
        self.llm = self._init_llm()
        self.chain = self._build_chain()
    
    def _init_llm(self):
        """Initialize LLM based on provider"""
        provider = LLM_PROVIDER.lower()
        
        if provider == "ollama":
            try:
                from langchain_ollama import ChatOllama
                return ChatOllama(model=LLM_MODEL)
            except ImportError:
                try:
                    from langchain_community.chat_models import ChatOllama
                    return ChatOllama(model=LLM_MODEL)
                except ImportError:
                    logger.error("Ollama not available. Install: pip install langchain-ollama")
                    raise
        
        elif provider == "huggingface":
            try:
                from langchain_community.llms import HuggingFacePipeline
                # This requires more setup - fallback to Ollama
                logger.warning("HuggingFace LLM requires more setup. Using Ollama fallback.")
                from langchain_community.chat_models import ChatOllama
                return ChatOllama(model="llama3.2")
            except Exception as e:
                logger.error(f"HuggingFace LLM error: {e}")
                raise
        
        elif provider == "nvidia":
            try:
                from langchain_nvidia_ai_endpoints import ChatNVIDIA
                return ChatNVIDIA(model=LLM_MODEL)
            except Exception as e:
                logger.error(f"NVIDIA LLM error: {e}")
                raise
        
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def _build_chain(self):
        """Build the RAG chain"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that answers questions about contracts and legal documents.
Answer based ONLY on the provided context. If the context doesn't contain enough information, say so.
Cite sources when referencing specific information."""),
            ("user", """Context:
{context}

Question: {question}

Answer:""")
        ])
        
        def format_docs(docs):
            return "\n\n".join([
                f"[Document {i+1} - {doc.metadata.get('filename', 'Unknown')}, Chunk {doc.metadata.get('chunk_index', i)}]\n{doc.page_content}"
                for i, doc in enumerate(docs)
            ])
        
        chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain
    
    def invoke_with_history(self, question: str, history: List[Dict] = None) -> Dict:
        """Answer a question with conversation history"""
        history = history or []
        
        # Format history for prompt
        history_text = "No previous conversation."
        if history:
            formatted = []
            for msg in history[-5:]:  # Last 5 exchanges
                human = msg.get("human", "")
                assistant = msg.get("assistant", "")
                if human:
                    formatted.append(f"Human: {human}")
                if assistant:
                    formatted.append(f"Assistant: {assistant}")
            history_text = "\n".join(formatted)
        
        # Build prompt with history
        prompt_with_history = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that answers questions about contracts and legal documents.
Answer based ONLY on the provided context and previous conversation. If the context doesn't contain enough information, say so.
Cite sources when referencing specific information."""),
            ("user", """Previous conversation:
{history}

Context:
{context}

Question: {question}

Answer:""")
        ])
        
        def format_docs(docs):
            return "\n\n".join([
                f"[Document {i+1} - {doc.metadata.get('filename', 'Unknown')}, Chunk {doc.metadata.get('chunk_index', i)}]\n{doc.page_content}"
                for i, doc in enumerate(docs)
            ])
        
        chain_with_history = (
            {
                "history": lambda x: history_text,
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | prompt_with_history
            | self.llm
            | StrOutputParser()
        )
        
        try:
            answer = chain_with_history.invoke(question)
            docs = self.retriever.invoke(question)
            sources = [
                {
                    "filename": doc.metadata.get("filename", "Unknown"),
                    "chunk_index": doc.metadata.get("chunk_index", "N/A"),
                    "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                for doc in docs
            ]
            
            return {
                "answer": str(answer),
                "sources": sources,
                "question": question
            }
        except Exception as e:
            logger.error(f"Error in RAG chain with history: {e}", exc_info=True)
            return {
                "answer": f"Error: {str(e)}",
                "sources": [],
                "question": question,
                "error": str(e)
            }
    
    def invoke(self, question: str) -> Dict:
        """Answer a question"""
        try:
            # Get answer
            answer = self.chain.invoke(question)
            
            # Get sources
            docs = self.retriever.invoke(question)
            sources = [
                {
                    "filename": doc.metadata.get("filename", "Unknown"),
                    "chunk_index": doc.metadata.get("chunk_index", "N/A"),
                    "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                for doc in docs
            ]
            
            return {
                "answer": str(answer),
                "sources": sources,
                "question": question
            }
        except Exception as e:
            logger.error(f"Error in RAG chain: {e}", exc_info=True)
            return {
                "answer": f"Error: {str(e)}",
                "sources": [],
                "question": question,
                "error": str(e)
            }
