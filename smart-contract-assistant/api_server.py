"""
FastAPI server for Smart Contract Assistant
"""
import logging
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import UPLOAD_DIR, API_PORT
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from rag_chain import RAGChain
from guardrails import Guardrails

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart Contract Assistant API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
doc_processor = DocumentProcessor()
vector_store_manager = VectorStoreManager()
rag_chain = None
guardrails = Guardrails()

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    global rag_chain
    # Try to load existing vector store
    if vector_store_manager.load_vector_store():
        retriever = vector_store_manager.get_retriever()
        rag_chain = RAGChain(retriever)
        logger.info("Loaded existing vector store")
    else:
        logger.info("No existing vector store found")

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "vector_store_loaded": rag_chain is not None
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a document"""
    global rag_chain
    
    # Validate file type
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    try:
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Processing file: {file.filename}")
        
        # Process document
        chunks = doc_processor.process_file(file_path)
        
        # Add to vector store
        if vector_store_manager.vector_store is None:
            vector_store_manager.create_vector_store(chunks)
        else:
            vector_store_manager.add_documents(chunks)
        
        # Update RAG chain
        retriever = vector_store_manager.get_retriever()
        rag_chain = RAGChain(retriever)
        
        return {
            "message": "File uploaded and processed successfully",
            "filename": file.filename,
            "chunks": len(chunks)
        }
    
    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/summarize")
async def summarize_document(filename: Optional[str] = None):
    """Summarize the uploaded document"""
    if rag_chain is None:
        raise HTTPException(status_code=400, detail="No documents loaded. Please upload a document first.")
    
    try:
        # Get summary by asking a summary question
        summary_question = "Provide a comprehensive summary of this document, including key terms, parties involved, main obligations, and important dates."
        result = rag_chain.invoke(summary_question)
        
        return {
            "summary": result["answer"],
            "sources": result.get("sources", [])
        }
    except Exception as e:
        logger.error(f"Error generating summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/qa")
async def question_answer(question: str, use_history: bool = False, history: List[dict] = None):
    """Answer a question with optional conversation history"""
    if rag_chain is None:
        raise HTTPException(status_code=400, detail="No documents loaded. Please upload a document first.")
    
    try:
        # Use history if provided
        if use_history and history:
            result = rag_chain.invoke_with_history(question, history)
        else:
            result = rag_chain.invoke(question)
        
        # Apply guardrails
        if guardrails.enabled and result.get("sources"):
            context = "\n".join([s.get("preview", "") for s in result["sources"]])
            guardrail_results = guardrails.validate_response(result["answer"], context)
            result["guardrails"] = guardrail_results
        
        return result
    except Exception as e:
        logger.error(f"Error answering question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
