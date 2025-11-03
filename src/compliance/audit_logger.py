# src/compliance/audit_logger.py
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List


class AuditLogger:
    """Log all system activities for compliance"""
    
    def __init__(self, log_path: str = "logs/audit.log"):
        self.log_path = log_path
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure JSON logger"""
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_path) if os.path.dirname(self.log_path) else ".", exist_ok=True)
        
        # Configure file handler
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        
        # Remove duplicate handlers
        if not self.audit_logger.handlers:
            handler = logging.FileHandler(self.log_path)
            
            # Custom JSON formatter
            class JSONFormatter(logging.Formatter):
                def format(self, record):
                    log_data = {
                        'timestamp': datetime.now().isoformat(),
                        'level': record.levelname,
                        'message': record.getMessage()
                    }
                    return json.dumps(log_data)
            
            handler.setFormatter(JSONFormatter())
            self.audit_logger.addHandler(handler)
    
    def log_query(self, user_id: str, query: str, results_count: int,
                 response_time_ms: float, model_used: str):
        """Log query execution"""
        
        event = {
            'event_type': 'QUERY_EXECUTED',
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'query_preview': query[:100],
            'query_length': len(query),
            'results_returned': results_count,
            'response_time_ms': response_time_ms,
            'model': model_used,
            'status': 'SUCCESS'
        }
        
        self.audit_logger.info(json.dumps(event))
    
    def log_security_event(self, user_id: str, event_type: str,
                          details: Dict[str, Any], severity: str = "MEDIUM"):
        """Log security-related events"""
        
        event = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'severity': severity,
            'details': details
        }
        
        self.audit_logger.warning(json.dumps(event))
    
    def log_data_access(self, user_id: str, documents_accessed: List[str],
                       purpose: str):
        """Log data access for GDPR compliance"""
        
        event = {
            'event_type': 'DATA_ACCESS',
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'documents_count': len(documents_accessed),
            'documents': documents_accessed,
            'purpose': purpose,
            'gdpr_compliant': True
        }
        
        self.audit_logger.info(json.dumps(event))
    
    def log_data_deletion(self, user_id: str, documents_deleted: List[str]):
        """Log data deletion for GDPR compliance"""
        
        event = {
            'event_type': 'DATA_DELETION',
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'documents_deleted': len(documents_deleted),
            'gdpr_right_to_forget': True
        }
        
        self.audit_logger.info(json.dumps(event))
