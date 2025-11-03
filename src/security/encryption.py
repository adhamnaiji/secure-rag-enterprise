# src/security/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

class SecureEncryption:
    """Handle document and data encryption"""
    
    def __init__(self, master_key: str):
        """Initialize encryption with master key"""
        self.salt = b'secure_rag_salt_'
        self.key = self._derive_key(master_key)
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(
            kdf.derive(password.encode())
        )
        return key
    
    def encrypt_document(self, document_text: str) -> str:
        """Encrypt document content"""
        return self.cipher.encrypt(document_text.encode()).decode()
    
    def decrypt_document(self, encrypted_text: str) -> str:
        """Decrypt document content"""
        return self.cipher.decrypt(encrypted_text.encode()).decode()
    
    def encrypt_embeddings(self, embeddings: list) -> str:
        """Encrypt vector embeddings"""
        import json
        json_str = json.dumps(embeddings)
        return self.cipher.encrypt(json_str.encode()).decode()
    
    def decrypt_embeddings(self, encrypted_embeddings: str) -> list:
        """Decrypt vector embeddings"""
        import json
        decrypted = self.cipher.decrypt(encrypted_embeddings.encode()).decode()
        return json.loads(decrypted)



