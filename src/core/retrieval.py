# src/core/retrieval.py
from typing import List, Tuple
from langchain_core.documents import Document  # ✓ Correct import for Document class
import numpy as np


class IntelligentRetriever:
    """Retrieve relevant documents with ranking & filtering"""
    
    def __init__(self, vector_store, embedding_model):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
    
    def retrieve_with_ranking(self, query: str, k: int = 5, 
                             similarity_threshold: float = 0.5) -> List[Tuple[Document, float]]:
        """
        Retrieve documents with intelligent ranking
        
        Combines:
        - Semantic similarity
        - Relevance scoring
        - Diversity filtering
        - Quality assessment
        """
        
        # 1. Semantic search
        docs_with_scores = self.vector_store.similarity_search_with_score(
            query, k=k*2  # Get more to filter
        )
        
        # 2. Filter by similarity threshold
        filtered_docs = [
            (doc, score) for doc, score in docs_with_scores 
            if (1 - score) >= similarity_threshold  # Convert to similarity
        ]
        
        # 3. Diversity filtering (avoid redundant documents)
        diverse_docs = self._filter_diversity(filtered_docs)
        
        # 4. Quality ranking
        ranked_docs = sorted(
            diverse_docs,
            key=lambda x: self._calculate_quality_score(x[0], query),  # ✓ Fixed tuple unpacking
            reverse=True
        )
        
        return ranked_docs[:k]
    
    def _filter_diversity(self, docs_with_scores: List[Tuple[Document, float]],
                         diversity_threshold: float = 0.3) -> List[Tuple[Document, float]]:
        """Remove redundant/similar documents"""
        
        if not docs_with_scores:
            return []
        
        diverse_docs = [docs_with_scores[0]]  # ✓ Fixed - should be first element, not entire list
        
        for doc, score in docs_with_scores[1:]:
            # Check similarity with already selected docs
            is_diverse = True
            for selected_doc, _ in diverse_docs:
                similarity = self._cosine_similarity(
                    doc.page_content,
                    selected_doc.page_content
                )
                if similarity > (1 - diversity_threshold):
                    is_diverse = False
                    break
            
            if is_diverse:
                diverse_docs.append((doc, score))
        
        return diverse_docs
    
    def _calculate_quality_score(self, doc: Document, query: str) -> float:
        """Calculate document quality score"""
        
        score = 0.0
        
        # Factor 1: Content length (well-developed document)
        if len(doc.page_content) > 500:
            score += 0.3
        
        # Factor 2: Query keyword presence
        query_words = set(query.lower().split())
        doc_words = set(doc.page_content.lower().split())
        keyword_overlap = len(query_words & doc_words) / len(query_words) if query_words else 0
        score += 0.4 * keyword_overlap
        
        # Factor 3: Metadata quality (recent documents)
        if 'timestamp' in doc.metadata:
            score += 0.3
        
        return score
    
    @staticmethod
    def _cosine_similarity(text1: str, text2: str) -> float:
        """Calculate cosine similarity between texts"""
        # Simplified: word-level similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0
