from datetime import datetime
from typing import Dict, Tuple
import re

import numpy as np

class AdversarialDetector:
    """Detect and mitigate adversarial attacks"""
    
    def __init__(self):
        self.attack_patterns = self._load_attack_patterns()
        self.suspicious_activity_log = []
    
    def _load_attack_patterns(self) -> Dict:
        """Load known adversarial patterns"""
        return {
            'prompt_injection': [
                r'ignore.*previous',
                r'system.*prompt',
                r'admin.*mode',
                r'instructions.*override',
                r'execute.*command'
            ],
            'data_extraction': [
                r'show.*training.*data',
                r'extract.*embeddings',
                r'dump.*knowledge',
                r'access.*internal'
            ],
            'model_inversion': [
                r'reconstruct.*original',
                r'invert.*function',
                r'reverse.*engineer'
            ],
            'jailbreak': [
                r'do.*anything.*now',
                r'unrestricted.*mode',
                r'disable.*safety',
                r'bypass.*restrictions'
            ]
        }
    
    def detect_adversarial_query(self, query: str) -> Tuple[bool, str, str]:
        """
        Detect if query contains adversarial patterns
        
        Returns:
            (is_adversarial, attack_type, confidence_level)
        """
        
        query_lower = query.lower()
        
        for attack_type, patterns in self.attack_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    # Log suspicious activity
                    self.suspicious_activity_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'query': query[:100],
                        'attack_type': attack_type,
                        'pattern_matched': pattern
                    })
                    
                    return True, attack_type, 'HIGH'
        
        return False, 'NONE', 'LOW'
    
    def test_robustness_against_perturbation(self, original_query: str,
                                            retriever) -> Dict:
        """Test system robustness against query perturbations"""
        
        perturbations = [
            original_query.lower(),  # Case change
            original_query.replace(',', ' '),  # Punctuation removal
            ' '.join(original_query.split()[::-1]),  # Word order reversal
            original_query.replace('the ', ''),  # Stop word removal
        ]
        
        results = {
            'original_ranking': [],
            'perturbed_rankings': [],
            'consistency_score': 0
        }
        
        # Get original ranking
        original_docs = retriever.retrieve_with_ranking(original_query, k=5)
        results['original_ranking'] = [doc.metadata.get('source') for doc, _ in original_docs]
        
        # Test perturbations
        for perturbed in perturbations:
            perturbed_docs = retriever.retrieve_with_ranking(perturbed, k=5)
            perturbed_ranking = [doc.metadata.get('source') for doc, _ in perturbed_docs]
            results['perturbed_rankings'].append(perturbed_ranking)
        
        # Calculate consistency
        consistency_scores = [
            len(set(results['original_ranking']) & set(prank)) / len(set(results['original_ranking']))
            for prank in results['perturbed_rankings']
        ]
        
        results['consistency_score'] = np.mean(consistency_scores) if consistency_scores else 0
        
        return results

