# src/security/input_validation.py
import os
import re
from typing import Dict, List, Tuple

class SecurityValidator:
    """Validate and sanitize inputs"""
    
    @staticmethod
    def validate_query(query: str, max_length: int = 1000) -> Tuple[bool, str]:
        """Validate user query"""
        if not query or len(query) == 0:
            return False, "Query cannot be empty"
        
        if len(query) > max_length:
            return False, f"Query exceeds maximum length of {max_length}"
        
        # Detect prompt injection patterns
        injection_patterns = [
            r'ignore.*instruction',
            r'system.*prompt',
            r'administrator.*mode',
            r'override.*security',
            r'bypass',
            r'exec\(',
            r'eval\('
        ]
        
        query_lower = query.lower()
        for pattern in injection_patterns:
            if re.search(pattern, query_lower):
                return False, f"Potentially malicious pattern detected: {pattern}"
        
        return True, ""
    
    @staticmethod
    def sanitize_document(document_text: str) -> str:
        """Remove potentially harmful content from documents"""
        # Remove script tags
        document_text = re.sub(r'<script[^>]*>.*?</script>', '', document_text, flags=re.DOTALL)
        
        # Remove SQL-like patterns
        document_text = re.sub(r"(\bDROP\b|\bDELETE\b|\bINSERT\b).*?;", '', document_text, flags=re.IGNORECASE)
        
        return document_text.strip()
    
    @staticmethod
    def validate_document(file_path: str) -> Tuple[bool, str]:
        """Validate document before processing"""
        # Check file size (max 50MB)
        if os.path.getsize(file_path) > 50 * 1024 * 1024:
            return False, "Document exceeds maximum size of 50MB"
        
        # Check file extension
        allowed_extensions = ['.pdf', '.txt', '.docx', '.md']
        if not any(file_path.endswith(ext) for ext in allowed_extensions):
            return False, f"File type not allowed. Allowed: {allowed_extensions}"
        
        return True, ""