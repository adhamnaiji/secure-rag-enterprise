import os
from typing import List, Dict, Optional
# Prefer 'pypdf' but fall back to 'PyPDF2' if 'pypdf' isn't installed.
try:
    from pypdf import PdfReader
except Exception:
    try:
        from PyPDF2 import PdfReader
    except Exception:
        raise ImportError("PdfReader not found. Install with: pip install pypdf or pip install PyPDF2")
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from src.security.encryption import SecureEncryption
from src.security.input_validation import SecurityValidator

class SecureDocumentProcessor:
    """Process documents securely with encryption"""
    
    def __init__(self, encryption_key: str):
        self.encryption = SecureEncryption(encryption_key)
        self.validator = SecurityValidator()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def process_pdf_secure(self, file_path: str) -> List[Dict]:
        """Process PDF with security checks"""
        
        # 1. Validate file
        is_valid, error_msg = self.validator.validate_document(file_path)
        if not is_valid:
            raise ValueError(f"Document validation failed: {error_msg}")
        
        # 2. Extract text
        documents = []
        try:
            pdf_reader = PdfReader(file_path)
            text_content = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text_content += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
            # 3. Sanitize content
            sanitized_text = self.validator.sanitize_document(text_content)
            
            # 4. Split into chunks
            chunks = self.text_splitter.split_text(sanitized_text)
            
            # 5. Create document objects with metadata
            for i, chunk in enumerate(chunks):
                doc = {
                    'id': f"{file_path}_{i}",
                    'content': chunk,
                    'source': file_path,
                    'chunk_index': i,
                    'timestamp': datetime.now().isoformat(),
                    'encrypted_content': self.encryption.encrypt_document(chunk)
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            raise RuntimeError(f"PDF processing error: {str(e)}")
    
    def process_batch_secure(self, directory_path: str) -> List[Dict]:
        """Process multiple documents securely"""
        all_documents = []
        
        for file_path in os.listdir(directory_path):
            if file_path.endswith('.pdf'):
                full_path = os.path.join(directory_path, file_path)
                try:
                    docs = self.process_pdf_secure(full_path)
                    all_documents.extend(docs)
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
        
        return all_documents