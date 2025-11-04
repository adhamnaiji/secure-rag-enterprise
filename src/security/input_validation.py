import os
import re
from typing import Tuple

class SecurityValidator:
    @staticmethod
    def validate_query(query: str, max_length: int = 1000) -> Tuple[bool, str]:
        if not query or len(query) == 0:
            return False, "Query cannot be empty"
        if len(query) > max_length:
            return False, "Query exceeds maximum length"
        patterns = [r'ignore.*instruction', r'system.*prompt', r'administrator.*mode', r'override.*security', r'bypass', r'exec\(', r'eval\(']
        for p in patterns:
            if re.search(p, query.lower()):
                return False, "Malicious pattern detected"
        return True, ""
    
    @staticmethod
    def sanitize_document(document_text: str) -> str:
        document_text = re.sub(r'<script[^>]*>.*?</script>', '', document_text, flags=re.DOTALL)
        document_text = re.sub(r"(\bDROP\b|\bDELETE\b|\bINSERT\b).*?;", '', document_text, flags=re.IGNORECASE)
        return document_text.strip()
    
    @staticmethod
    def validate_document(file_path: str) -> Tuple[bool, str]:
        if not os.path.exists(file_path):
            return False, "File not found"
        if os.path.getsize(file_path) > 50 * 1024 * 1024:
            return False, "File too large"
        exts = ['.pdf', '.txt', '.docx', '.md']
        if not any(file_path.endswith(e) for e in exts):
            return False, "Invalid file type"
        return True, ""
