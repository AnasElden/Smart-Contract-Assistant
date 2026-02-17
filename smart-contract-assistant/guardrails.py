"""
Guardrails for safety and factuality checking
"""
import logging
from typing import Dict, List
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class Guardrails:
    """Simple guardrails for response validation"""
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.enabled = True
    
    def validate_response(self, answer: str, context: str) -> Dict:
        """
        Validate response against context for factuality
        
        Args:
            answer: Generated answer
            context: Source context from documents
            
        Returns:
            Dictionary with validation results
        """
        if not self.enabled:
            return {"all_passed": True, "checks": []}
        
        checks = []
        
        # Check 1: Answer should reference context
        answer_lower = answer.lower()
        context_lower = context.lower()
        
        # Simple keyword overlap check
        answer_words = set(answer_lower.split())
        context_words = set(context_lower.split())
        common_words = answer_words.intersection(context_words)
        
        relevance_score = len(common_words) / max(len(answer_words), 1)
        has_relevance = relevance_score > 0.1
        
        checks.append({
            "check": "context_relevance",
            "passed": has_relevance,
            "score": relevance_score,
            "message": "Answer references context" if has_relevance else "Answer may not be grounded in context"
        })
        
        # Check 2: Answer should not be too generic
        generic_phrases = [
            "i don't know",
            "i cannot answer",
            "no information",
            "not available",
            "unable to provide"
        ]
        is_generic = any(phrase in answer_lower for phrase in generic_phrases)
        
        checks.append({
            "check": "specificity",
            "passed": not is_generic,
            "message": "Answer is specific" if not is_generic else "Answer is too generic"
        })
        
        # Check 3: Answer should not be empty
        has_content = len(answer.strip()) > 10
        
        checks.append({
            "check": "has_content",
            "passed": has_content,
            "message": "Answer has content" if has_content else "Answer is too short"
        })
        
        all_passed = all(check["passed"] for check in checks)
        
        return {
            "all_passed": all_passed,
            "checks": checks,
            "relevance_score": relevance_score
        }

