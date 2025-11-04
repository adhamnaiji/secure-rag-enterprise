from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List, Dict, Optional
import logging
import torch

logger = logging.getLogger(__name__)


class VectorStoreHandler:
    """Handle vector store operations"""
    
    def __init__(self):
        try:
            # Force CPU usage
            torch.set_default_device("cpu")
            
            # Initialize embeddings (HuggingFace - FREE, LOCAL)
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-miniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
            self.vector_store = None
            logger.info("✅ Vector store initialized with HuggingFace")
        except Exception as e:
            logger.error(f"❌ Failed to initialize embeddings: {e}")
            self.embeddings = None
            self.vector_store = None
    
    def create_from_documents(self, documents: List[Dict]) -> bool:
        """Create vector store from documents"""
        try:
            if not self.embeddings:
                logger.error("❌ Embeddings not initialized")
                return False
            
            if not documents:
                logger.warning("⚠️ No documents to process")
                return False
            
            # Extract texts and metadata
            texts = []
            metadatas = []
            
            for doc in documents:
                if isinstance(doc, dict):
                    content = doc.get('content', '')
                else:
                    content = str(doc)
                
                if content:
                    texts.append(content)
                    metadatas.append({
                        'source': doc.get('source', 'unknown') if isinstance(doc, dict) else 'unknown',
                        'chunk_index': doc.get('chunk_index', 0) if isinstance(doc, dict) else 0,
                    })
            
            if not texts:
                logger.warning("⚠️ No text content found")
                return False
            
            # Create FAISS vector store
            self.vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"✅ Vector store created with {len(texts)} documents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating vector store: {e}", exc_info=True)
            return False
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search vector store for similar documents"""
        try:
            if not self.vector_store:
                logger.warning("⚠️ Vector store is empty")
                return []
            
            # Search with similarity score
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': float(score)
                })
            
            logger.info(f"✅ Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error searching vector store: {e}", exc_info=True)
            return []
    
    def add_documents(self, documents: List[Dict]) -> bool:
        """Add documents to existing vector store"""
        try:
            if not self.vector_store:
                logger.warning("⚠️ Creating new vector store")
                return self.create_from_documents(documents)
            
            texts = [doc.get('content', '') if isinstance(doc, dict) else str(doc) for doc in documents]
            metadatas = [doc.get('metadata', {}) if isinstance(doc, dict) else {} for doc in documents]
            
            self.vector_store.add_texts(texts=texts, metadatas=metadatas)
            logger.info(f"✅ Added {len(texts)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding documents: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if vector store is ready"""
        return self.vector_store is not None and self.embeddings is not None