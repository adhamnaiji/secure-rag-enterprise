from typing import Tuple
import re

class AdversarialDetector:
    def __init__(self):
        self.patterns = {
            'injection': [r'ignore.*previous', r'system.*prompt', r'admin.*mode'],
            'extraction': [r'show.*training', r'extract.*embedding'],
            'jailbreak': [r'unrestricted', r'disable.*safety']
        }
    
    def detect_adversarial_query(self, query: str) -> Tuple[bool, str, float]:
        query_lower = query.lower()
        for attack_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return True, attack_type, 0.95
        return False, "none", 0.0
