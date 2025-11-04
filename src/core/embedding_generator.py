from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import Dict, List, Optional

class SecureEmbeddingGenerator:
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-miniLM-L6-v2")
        self.vector_store = None
    
    def generate_embeddings(self, documents: List[Dict]) -> FAISS:
        texts = [doc['content'] for doc in documents]
        metadatas = [{'source': doc['source'], 'chunk_index': doc['chunk_index'], 'timestamp': doc['timestamp']} for doc in documents]
        self.vector_store = FAISS.from_texts(texts=texts, embedding=self.embeddings, metadatas=metadatas)
        return self.vector_store
    
    def save_vector_store_secure(self, path: str):
        self.vector_store.save_local(path)
