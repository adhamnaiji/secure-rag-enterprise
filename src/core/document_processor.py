# src/rag/document_processor.py
import os
import re
from typing import List, Dict, Optional
from langchain.embeddings import OpenAIEmbeddings
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from typing import List

class SecureDocumentProcessor:
    """Process financial documents securely for RAG"""
    
    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        try:
            self.embeddings = OpenAIEmbeddings(model=embedding_model)
        except Exception as e:
            print(f"⚠️ Warning: OpenAI embeddings not available. Using local embeddings.")
            # Fallback to local embeddings
            from langchain.embeddings import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-miniLM-L6-v2"
            )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " "]
        )
        self.vector_store = None
        self.processing_log = []
        self.documents_loaded = []
    
    def load_documents(self, folder_path: str) -> List[Dict]:
        """
        Load ALL documents from a folder (PDF and TXT)
        
        Args:
            folder_path: Path to folder containing documents
            
        Returns:
            List of processed documents
        """
        print(f"📂 Loading documents from: {folder_path}")
        
        if not os.path.exists(folder_path):
            print(f"❌ Folder not found: {folder_path}")
            return []
        
        documents = []
        files = os.listdir(folder_path)
        
        print(f"📋 Found {len(files)} files")
        
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            
            if not os.path.isfile(file_path):
                continue
            
            try:
                print(f"⏳ Processing: {file_name}...", end=" ")
                
                # Load based on file type
                if file_name.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                
                elif file_name.endswith('.txt'):
                    loader = TextLoader(file_path)
                    docs = loader.load()
                
                else:
                    print("⏭️ SKIPPED (unsupported format)")
                    continue
                
                # Process each document
                for doc in docs:
                    # Sanitize content
                    content = self._sanitize_content(doc.page_content)
                    
                    documents.append({
                        'content': content,
                        'source': file_name,
                        'page': doc.metadata.get('page', 0),
                        'sanitized': True,
                        'loaded_at': datetime.now().isoformat()
                    })
                
                self.processing_log.append({
                    'file': file_name,
                    'status': 'success',
                    'docs_processed': len(docs),
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f"✅ SUCCESS ({len(docs)} chunks)")
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                self.processing_log.append({
                    'file': file_name,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        print(f"\n📊 Total documents loaded: {len(documents)}")
        self.documents_loaded = documents
        return documents
    
    def _sanitize_content(self, content: str) -> str:
        """Remove sensitive patterns from content"""
        # Mask credit card numbers
        content = re.sub(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', 
                        '[MASKED_CARD]', content)
        
        # Mask SSN
        content = re.sub(r'\d{3}-\d{2}-\d{4}', '[MASKED_SSN]', content)
        
        # Mask email addresses
        content = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                        '[MASKED_EMAIL]', content)
        
        return content
    
    def create_vector_store(self, documents: List[Dict]) -> Optional[FAISS]:
        """
        Create FAISS vector store from documents
        
        Args:
            documents: Processed documents
            
        Returns:
            FAISS vector store or None if empty
        """
        if not documents:
            print("❌ ERROR: No documents provided to create vector store")
            return None
        
        print(f"\n🔄 Creating vector store from {len(documents)} documents...")
        
        # Extract content from documents
        texts = [doc['content'] for doc in documents]
        
        # Split into chunks
        all_chunks = []
        all_metadata = []
        
        print(f"✂️ Splitting documents into chunks...")
        for i, text in enumerate(texts):
            chunks = self.text_splitter.split_text(text)
            all_chunks.extend(chunks)
            
            # Create metadata for each chunk
            for chunk in chunks:
                all_metadata.append({
                    'source': documents[i]['source'],
                    'page': documents[i].get('page', 0),
                    'loaded_at': documents[i].get('loaded_at', '')
                })
        
        print(f"📦 Total chunks created: {len(all_chunks)}")
        
        if not all_chunks:
            print("❌ ERROR: No chunks created. Vector store is empty.")
            return None
        
        try:
            print(f"🧠 Generating embeddings for {len(all_chunks)} chunks...")
            
            # Create vector store
            self.vector_store = FAISS.from_texts(
                texts=all_chunks,
                embedding=self.embeddings,
                metadatas=all_metadata
            )
            
            print(f"✅ Vector store created successfully!")
            print(f"📊 Vector store contains {len(all_chunks)} indexed chunks")
            
            return self.vector_store
        
        except Exception as e:
            print(f"❌ ERROR creating vector store: {str(e)}")
            return None
    
    def retrieve_similar_documents(self, query: str, k: int = 5) -> List[Dict]:
        """
        Retrieve relevant documents using semantic similarity
        
        Args:
            query: User query
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        if self.vector_store is None:
            print("❌ Vector store is empty. Please load documents first.")
            return []
        
        print(f"\n🔍 Searching for: '{query}'")
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            if not results:
                print("❌ No results found")
                return []
            
            retrieved_docs = []
            for i, (doc, score) in enumerate(results):
                retrieved_docs.append({
                    'rank': i + 1,
                    'content': doc.page_content[:300],
                    'similarity_score': float(score),
                    'source': doc.metadata.get('source', 'unknown'),
                    'page': doc.metadata.get('page', 0)
                })
                print(f"  {i+1}. {doc.metadata.get('source')} (Score: {score:.3f})")
            
            return retrieved_docs
        
        except Exception as e:
            print(f"❌ ERROR during retrieval: {str(e)}")
            return []
    
    def save_vector_store(self, path: str = "data/vectors"):
        """Save vector store to disk"""
        if self.vector_store is None:
            print("❌ Vector store is empty. Cannot save.")
            return
        
        os.makedirs(path, exist_ok=True)
        self.vector_store.save_local(path)
        print(f"✅ Vector store saved to {path}")
    
    def load_vector_store(self, path: str = "data/vectors"):
        """Load vector store from disk"""
        if not os.path.exists(path):
            print(f"❌ Vector store not found at {path}")
            return None
        
        self.vector_store = FAISS.load_local(path, self.embeddings)
        print(f"✅ Vector store loaded from {path}")
        return self.vector_store
