from collections import defaultdict
from typing import Dict, List

class FairnessMonitor:
    """Monitor for bias and fairness issues"""
    
    def __init__(self):
        self.query_patterns_by_demographic = defaultdict(list)
    
    def analyze_response_bias(self, query: str, response: str,
                             protected_attributes: Dict) -> Dict:
        """Analyze if response contains bias"""
        
        bias_indicators = {
            'gender': ['he', 'she', 'man', 'woman', 'male', 'female'],
            'age': ['young', 'old', 'elderly', 'millennial', 'boomer'],
            'race': ['white', 'black', 'asian', 'hispanic', 'middle eastern']
        }
        
        results = {
            'query': query,
            'biases_detected': [],
            'bias_score': 0.0,
            'recommendation': 'NEUTRAL'
        }
        
        for attribute, indicators in bias_indicators.items():
            if attribute not in protected_attributes:
                continue
            
            count = sum(1 for indicator in indicators 
                       if indicator.lower() in response.lower())
            
            if count > 0:
                results['biases_detected'].append({
                    'attribute': attribute,
                    'count': count,
                    'indicators': [ind for ind in indicators if ind.lower() in response.lower()]
                })
                results['bias_score'] += count / len(indicators)
        
        if results['bias_score'] > 0.5:
            results['recommendation'] = 'HIGH_BIAS_DETECTED'
        elif results['bias_score'] > 0.2:
            results['recommendation'] = 'MODERATE_BIAS'
        
        return results
