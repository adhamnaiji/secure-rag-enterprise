from typing import Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> Tuple[bool, str]:
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        self.requests[user_id] = [t for t in self.requests[user_id] if t > window_start]
        if len(self.requests[user_id]) >= self.max_requests:
            return False, "Rate limit exceeded"
        self.requests[user_id].append(now)
        return True, "Request allowed"
    
    def get_remaining_requests(self, user_id: str) -> int:
        return max(0, self.max_requests - len(self.requests[user_id]))
