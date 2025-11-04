# src/rag/document_processor.py - PERPLEXITY OPTIMIZED
import os
import re
from typing import List, Dict, Optional
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)


class SecureDocumentProcessor:
    """Process documents securely for RAG with Perplexity integration"""
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-miniLM-L6-v2"):
        """
        Initialize document processor
        
        Args:
            embedding_model: HuggingFace embedding model (FREE - no API key needed)
        """
        try:
            # Use local HuggingFace embeddings (NO OpenAI dependency)
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model
            )
            logger.info(f"✅ Embeddings initialized: {embedding_model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize embeddings: {e}")
            raise
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
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
        logger.info(f"📂 Loading documents from: {folder_path}")
        
        if not os.path.exists(folder_path):
            logger.error(f"❌ Folder not found: {folder_path}")
            return []
        
        documents = []
        files = os.listdir(folder_path)
        
        logger.info(f"📋 Found {len(files)} files")
        
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            
            if not os.path.isfile(file_path):
                continue
            
            try:
                logger.info(f"⏳ Processing: {file_name}...")
                
                # Load based on file type
                if file_name.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                
                elif file_name.endswith('.txt'):
                    loader = TextLoader(file_path, encoding='utf-8')
                    docs = loader.load()
                
                else:
                    logger.warning(f"⏭️  SKIPPED: {file_name} (unsupported format)")
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
                
                logger.info(f"✅ SUCCESS: {file_name} ({len(docs)} chunks)")
                
            except Exception as e:
                logger.error(f"❌ ERROR processing {file_name}: {str(e)}")
                self.processing_log.append({
                    'file': file_name,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        logger.info(f"📊 Total documents loaded: {len(documents)}")
        self.documents_loaded = documents
        return documents
    
    def _sanitize_content(self, content: str) -> str:
        """Remove sensitive patterns from content"""
        
        # Mask credit card numbers
        content = re.sub(
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            '[MASKED_CC]',
            content
        )
        
        # Mask SSN
        content = re.sub(
            r'\b\d{3}-\d{2}-\d{4}\b',
            '[MASKED_SSN]',
            content
        )
        
        # Mask emails
        content = re.sub(
            r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            '[MASKED_EMAIL]',
            content
        )
        
        # Mask phone numbers
        content = re.sub(
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            '[MASKED_PHONE]',
            content
        )
        
        return content
    
    def create_vector_store(self, documents: List[Dict]) -> Optional[FAISS]:
        """
        Create FAISS vector store from documents
        
        Args:
            documents: Processed documents
            
        Returns:
            FAISS vector store or None if error
        """
        if not documents:
            logger.error("❌ No documents provided")
            return None
        
        logger.info(f"🔄 Creating vector store from {len(documents)} documents...")
        
        # Extract content
        texts = [doc['content'] for doc in documents]
        
        # Split into chunks
        all_chunks = []
        all_metadata = []
        
        logger.info("✂️  Splitting documents into chunks...")
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
        
        logger.info(f"📦 Total chunks: {len(all_chunks)}")
        
        if not all_chunks:
            logger.error("❌ No chunks created")
            return None
        
        try:
            logger.info(f"🧠 Generating embeddings for {len(all_chunks)} chunks...")
            
            # Create vector store (uses HuggingFace embeddings - FREE!)
            self.vector_store = FAISS.from_texts(
                texts=all_chunks,
                embedding=self.embeddings,
                metadatas=all_metadata
            )
            
            logger.info(f"✅ Vector store created successfully!")
            logger.info(f"📊 {len(all_chunks)} chunks indexed")
            
            return self.vector_store
        
        except Exception as e:
            logger.error(f"❌ Error creating vector store: {str(e)}")
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
            logger.warning("❌ Vector store is empty")
            return []
        
        logger.info(f"🔍 Searching: '{query}'")
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            if not results:
                logger.warning("⚠️  No results found")
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
                logger.info(f"  {i+1}. {doc.metadata.get('source')} (Score: {score:.3f})")
            
            return retrieved_docs
        
        except Exception as e:
            logger.error(f"❌ Error during retrieval: {str(e)}")
            return []
    
    def save_vector_store(self, path: str = "data/vectors") -> bool:
        """Save vector store to disk"""
        if self.vector_store is None:
            logger.error("❌ Vector store is empty")
            return False
        
        try:
            os.makedirs(path, exist_ok=True)
            self.vector_store.save_local(path)
            logger.info(f"✅ Vector store saved to {path}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving vector store: {e}")
            return False
    
    def load_vector_store(self, path: str = "data/vectors") -> Optional[FAISS]:
        """Load vector store from disk"""
        if not os.path.exists(path):
            logger.error(f"❌ Vector store not found at {path}")
            return None
        
        try:
            self.vector_store = FAISS.load_local(path, self.embeddings)
            logger.info(f"✅ Vector store loaded from {path}")
            return self.vector_store
        except Exception as e:
            logger.error(f"❌ Error loading vector store: {e}")
            return None
