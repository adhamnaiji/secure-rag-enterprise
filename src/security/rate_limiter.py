from typing import Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    """Implement rate limiting for API protection"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)  # user_id -> [timestamps]
    
    def is_allowed(self, user_id: str) -> Tuple[bool, str]:
        """Check if request is allowed"""
        
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False, f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds}s"
        
        # Record request
        self.requests[user_id].append(now)
        return True, "Request allowed"
    
    def get_remaining_requests(self, user_id: str) -> int:
        """Get remaining requests for user"""
        return max(0, self.max_requests - len(self.requests[user_id]))