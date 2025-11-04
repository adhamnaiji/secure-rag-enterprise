import hashlib
import base64
from cryptography.fernet import Fernet

class SecureEncryption:
    def __init__(self, master_key: str):
        self.salt = b'secure_rag_salt_'
        self.key = self._derive_key(master_key)
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        key_material = hashlib.pbkdf2_hmac('sha256', password.encode(), self.salt, 100000)
        return base64.urlsafe_b64encode(key_material)
    
    def encrypt_document(self, document_text: str) -> str:
        return self.cipher.encrypt(document_text.encode()).decode()
    
    def decrypt_document(self, encrypted_text: str) -> str:
        return self.cipher.decrypt(encrypted_text.encode()).decode()
    
    def encrypt_embeddings(self, embeddings: list) -> str:
        import json
        return self.cipher.encrypt(json.dumps(embeddings).encode()).decode()
    
    def decrypt_embeddings(self, encrypted_embeddings: str) -> list:
        import json
        return json.loads(self.cipher.decrypt(encrypted_embeddings.encode()).decode())
