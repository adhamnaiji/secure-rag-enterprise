import re
from typing import Tuple


class SecurityValidator:
    """Validates queries for security threats"""
    
    # SQL Injection keywords to block
    SQL_KEYWORDS = {
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT',
        'UPDATE', 'EXEC', 'EXECUTE', 'UNION', 'SELECT', 'FROM',
        'WHERE', 'HAVING', 'GROUP', 'ORDER', 'SCRIPT', 'JAVASCRIPT',
        'WAITFOR', 'DECLARE', 'SET', 'CAST', 'CONVERT', 'WAITFOR',
        'DBCC', 'BACKUP', 'RESTORE', 'LOAD'
    }
    
    # Dangerous characters for SQL injection
    DANGEROUS_CHARS = [';', '--', '/*', '*/', 'xp_', 'sp_']
    
    # Prompt injection patterns
    JAILBREAK_PATTERNS = [
        r'ignore.*instruction',
        r'system.*prompt',
        r'administrator.*mode',
        r'override.*security',
        r'bypass.*protection',
        r'disregard.*guideline',
        r'forget.*previous',
        r'pretend.*you.*are',
        r'\[SYSTEM',
        r'DAN:',
        r'developer.*mode',
        r'unrestricted.*ai',
    ]
    
    @staticmethod
    def validate_query(query: str, max_length: int = 1000) -> Tuple[bool, str]:
        """
        Validate query for SQL injection and malicious patterns
        
        Returns: (is_valid, error_message)
        """
        
        if not query or len(query) == 0:
            return False, "Query cannot be empty"
        
        if len(query) > max_length:
            return False, "Query exceeds maximum length"
        
        query_upper = query.upper().strip()
        
        # ===== CHECK 1: SQL INJECTION KEYWORDS =====
        for keyword in SecurityValidator.SQL_KEYWORDS:
            # Look for word boundaries to avoid false positives
            if re.search(r'\b' + keyword + r'\b', query_upper):
                return False, f"SQL injection pattern detected - {keyword}"
        
        # ===== CHECK 2: SQL DANGEROUS CHARACTERS =====
        for dangerous in SecurityValidator.DANGEROUS_CHARS:
            if dangerous in query:
                return False, f"SQL injection pattern detected - forbidden character: {dangerous}"
        
        # ===== CHECK 3: SQL QUOTES + OPERATIONS =====
        # Look for patterns like: ' OR, ' AND, ' DROP
        if re.search(r"'\s*(OR|AND|UNION|DROP|DELETE|INSERT|UPDATE)\s*", query_upper):
            return False, "SQL injection pattern detected - quote manipulation"
        
        # ===== CHECK 4: PROMPT INJECTION / JAILBREAK =====
        for pattern in SecurityValidator.JAILBREAK_PATTERNS:
            if re.search(pattern, query.lower()):
                return False, "Prompt injection pattern detected - jailbreak attempt"
        
        # ===== CHECK 5: COMMON ENCODING ATTACKS =====
        # URL encoded SQL keywords
        if '%27' in query or '%3B' in query or '%2D%2D' in query:
            return False, "SQL injection pattern detected - encoded characters"
        
        # ===== CHECK 6: MULTIPLE SEMICOLONS =====
        if query.count(';') > 1:
            return False, "SQL injection pattern detected - multiple statements"
        
        # All checks passed
        return True, ""
    
    @staticmethod
    def sanitize_document(document_text: str) -> str:
        """Remove potentially dangerous content from documents"""
        # Remove script tags
        document_text = re.sub(r'<script.*?</script>', '', document_text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove event handlers
        document_text = re.sub(r'on\w+\s*=', '', document_text, flags=re.IGNORECASE)
        
        return document_text
