import os

fixed_content = '''import os
from typing import Optional
from datetime import datetime, timedelta, timezone
import jwt


class AccessController:
    """Handle authentication and authorization"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.token_expiry = timedelta(hours=1)
    
    def create_access_token(self, user_id: str) -> str:
        """Create JWT access token"""
        # Use timezone-aware datetime (Python 3.14+ compatible)
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "exp": now + self.token_expiry,
            "iat": now
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
'''

with open('src/security/access_control.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print('✅ Fixed: src/security/access_control.py')
print('✅ Removed datetime.utcnow() deprecation warnings')
print('✅ Python 3.14+ compatible')
