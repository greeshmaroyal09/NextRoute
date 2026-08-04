import time
from fastapi import Request, HTTPException

class RateLimiter:
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self._ip_history = {}

    def check(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Clean up old
        history = self._ip_history.get(client_ip, [])
        history = [t for t in history if now - t < 60]
        
        if len(history) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
            
        history.append(now)
        self._ip_history[client_ip] = history
        return True
        
rate_limiter = RateLimiter(requests_per_minute=20)
