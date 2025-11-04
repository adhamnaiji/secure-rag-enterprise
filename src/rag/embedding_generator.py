# embedding_generator.py - FIXED FREE EMBEDDINGS VERSION
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class EmbeddingGenerator:
    def __init__(self):
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-miniLM-L6-v2"
            )
            self.vector_store = None
        except Exception as e:
            print(f"Error: {str(e)}")
            self.embeddings = None
    
    def generate_embeddings(self, documents):
        """Generate embeddings for documents"""
        try:
            if not self.embeddings:
                return None, "Error: Embeddings not initialized"
            
            texts = [doc.page_content for doc in documents]
            self.vector_store = FAISS.from_texts(texts, self.embeddings)
            return self.vector_store, f"Successfully generated embeddings for {len(documents)} documents"
        except Exception as e:
            return None, f"Error generating embeddings: {str(e)}"
