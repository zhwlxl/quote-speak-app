import logging
import time
from functools import wraps

# Simple request timing decorator
def time_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{f.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return decorated_function

# Usage tracking
class UsageTracker:
    def __init__(self):
        self.requests = 0
        self.errors = 0
        self.total_generation_time = 0
        self.provider_usage = {}
    
    def track_request(self, success=True, generation_time=0, provider=None):
        self.requests += 1
        if not success:
            self.errors += 1
        self.total_generation_time += generation_time
        
        if provider:
            if provider not in self.provider_usage:
                self.provider_usage[provider] = 0
            self.provider_usage[provider] += 1
    
    def get_stats(self):
        return {
            'requests': self.requests,
            'errors': self.errors,
            'error_rate': self.errors / max(self.requests, 1),
            'avg_generation_time': self.total_generation_time / max(self.requests, 1),
            'provider_usage': self.provider_usage
        }