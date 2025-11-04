from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class VectorStoreHandler:
    """Handle vector store operations"""
    
    def __init__(self):
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-miniLM-L6-v2"
            )
            self.vector_store = None
            logger.info("Vector store initialized")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            self.embeddings = None
    
    def create_from_documents(self, documents: List[Dict]) -> bool:
        """Create vector store from documents"""
        try:
            if not self.embeddings:
                logger.error("Embeddings not available")
                return False
            
            texts = [doc.get('content', '') for doc in documents]
            metadatas = [
                {
                    'source': doc.get('source', 'unknown'),
                    'chunk_index': doc.get('chunk_index', 0),
                    'timestamp': doc.get('timestamp', '')
                }
                for doc in documents
            ]
            
            self.vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            logger.info(f"Vector store created with {len(documents)} documents")
            return True
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            return False
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search vector store"""
        try:
            if not self.vector_store:
                logger.warning("Vector store is empty")
                return []
            
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': float(score)
                }
                for doc, score in results
            ]
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
