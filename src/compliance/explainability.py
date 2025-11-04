from typing import Dict, List

class ExplainabilityTracker:
    def explain_retrieval(self, query: str, retrieved_docs: List, retrieval_scores: List) -> Dict:
        return {
            'query': query,
            'retrieval_explanation': [{'rank': i+1, 'source': getattr(d, 'metadata', {}).get('source', 'unknown') if d else 'N/A', 'snippet': getattr(d, 'page_content', '')[:100] if d else '', 'similarity_score': s, 'why_retrieved': f"Semantic similarity: {s:.2f}"} for i, (d, s) in enumerate(zip(retrieved_docs, retrieval_scores))],
            'ranking_factors': {'semantic_similarity': 0.4, 'keyword_overlap': 0.3, 'quality': 0.2, 'recency': 0.1}
        }
