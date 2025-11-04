import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

class AuditLogger:
    def __init__(self, log_path: str = "logs/audit.log"):
        self.log_path = log_path
        self._setup_logger()
    
    def _setup_logger(self):
        os.makedirs(os.path.dirname(self.log_path) if os.path.dirname(self.log_path) else ".", exist_ok=True)
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        if not self.audit_logger.handlers:
            handler = logging.FileHandler(self.log_path)
            class JSONFormatter(logging.Formatter):
                def format(self, record):
                    return json.dumps({'timestamp': datetime.now().isoformat(), 'level': record.levelname, 'message': record.getMessage()})
            handler.setFormatter(JSONFormatter())
            self.audit_logger.addHandler(handler)
    
    def log_query(self, user_id: str, query: str, results_count: int, response_time_ms: float, model_used: str):
        event = {'event_type': 'QUERY_EXECUTED', 'timestamp': datetime.now().isoformat(), 'user_id': user_id, 'query_preview': query[:100], 'results': results_count, 'time_ms': response_time_ms, 'model': model_used}
        self.audit_logger.info(json.dumps(event))
    
    def log_security_event(self, user_id: str, event_type: str, details: Dict[str, Any], severity: str = "MEDIUM"):
        event = {'event_type': event_type, 'timestamp': datetime.now().isoformat(), 'user_id': user_id, 'severity': severity, 'details': details}
        self.audit_logger.warning(json.dumps(event))
    
    def log_data_access(self, user_id: str, documents_accessed: List[str], purpose: str):
        event = {'event_type': 'DATA_ACCESS', 'timestamp': datetime.now().isoformat(), 'user_id': user_id, 'documents_count': len(documents_accessed), 'documents': documents_accessed, 'purpose': purpose}
        self.audit_logger.info(json.dumps(event))
    
    def log_data_deletion(self, user_id: str, documents_deleted: List[str]):
        event = {'event_type': 'DATA_DELETION', 'timestamp': datetime.now().isoformat(), 'user_id': user_id, 'documents_deleted': len(documents_deleted)}
        self.audit_logger.info(json.dumps(event))
