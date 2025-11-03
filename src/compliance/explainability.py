from typing import Dict, Tuple, List

class ExplainabilityTracker:
    """Track explainability for EU AI Act compliance"""
    
    def explain_retrieval(self, query: str, retrieved_docs: List,
                         retrieval_scores: List) -> Dict:
        """Explain why specific documents were retrieved"""
        
        explanation = {
            'query': query,
            'retrieval_explanation': [],
            'ranking_factors': {
                'semantic_similarity': 0.4,
                'keyword_overlap': 0.3,
                'document_quality': 0.2,
                'recency': 0.1
            }
        }
        
        for i, (doc, score) in enumerate(zip(retrieved_docs, retrieval_scores)):
            explanation['retrieval_explanation'].append({
                'rank': i + 1,
                'source': doc.metadata.get('source'),
                'snippet': doc.page_content[:100],
                'similarity_score': score,
                'why_retrieved': f"Semantic similarity: {score:.2f}, Contains keywords from query"
            })
        
        return explanation