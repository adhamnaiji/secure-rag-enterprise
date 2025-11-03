from core.document_processor import SecureDocumentProcessor


def test_document_processing():
    """Test end-to-end document processing"""
    processor = SecureDocumentProcessor("encryption_key")
    
    # Create test PDF
    test_file = "test_document.pdf"
    # ... create test PDF
    
    # Process
    docs = processor.process_pdf_secure(test_file)
    assert len(docs) > 0
    assert all('content' in doc for doc in docs)
    assert all('encrypted_content' in doc for doc in docs)