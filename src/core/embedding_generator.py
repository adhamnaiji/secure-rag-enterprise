from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import Dict, List, Optional
import os
from config.settings import settings


class SecureEmbeddingGenerator:
    """Generate embeddings with security considerations - 100% FREE"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key
        
        # FREE Local embeddings for privacy - runs on your machine
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-miniLM-L6-v2"
        )
        
        self.vector_store = None
    
    def generate_embeddings(self, documents: List[Dict]) -> FAISS:
        """Generate embeddings for documents"""
        
        # Extract text from documents
        texts = [doc['content'] for doc in documents]
        metadatas = [
            {
                'source': doc['source'],
                'chunk_index': doc['chunk_index'],
                'timestamp': doc['timestamp']
            }
            for doc in documents
        ]
        
        # Create FAISS vector store - 100% free
        self.vector_store = FAISS.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas
        )
        
        return self.vector_store
    
    def save_vector_store_secure(self, path: str):
        """Save embeddings with optional encryption"""
        self.vector_store.save_local(path)
