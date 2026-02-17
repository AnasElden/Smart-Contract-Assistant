"""
Simple document processor for PDF and DOCX files
"""
import logging
from pathlib import Path
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from docx import Document as DocxDocument
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

from config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process PDF and DOCX files into chunks"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
    
    def extract_text_pdf(self, file_path: Path) -> str:
        """Extract text from PDF"""
        if HAS_PYMUPDF:
            doc = fitz.open(file_path)
            text = "\n".join([page.get_text() for page in doc])
            doc.close()
            return text
        else:
            raise ValueError("PyMuPDF not installed. Install with: pip install pymupdf")
    
    def extract_text_docx(self, file_path: Path) -> str:
        """Extract text from DOCX"""
        if HAS_DOCX:
            doc = DocxDocument(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        else:
            raise ValueError("python-docx not installed. Install with: pip install python-docx")
    
    def process_file(self, file_path: Path) -> List[Document]:
        """Process a file and return chunks"""
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()
        
        # Extract text
        if suffix == ".pdf":
            text = self.extract_text_pdf(file_path)
        elif suffix == ".docx":
            text = self.extract_text_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        if not text.strip():
            raise ValueError(f"No text extracted from {file_path.name}")
        
        # Split into chunks
        chunks = self.text_splitter.create_documents(
            [text],
            metadatas=[{"filename": file_path.name, "source": str(file_path)}]
        )
        
        # Add chunk index
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
        
        logger.info(f"Created {len(chunks)} chunks from {file_path.name}")
        return chunks
