"""
Rate Limiting Service
Implements token bucket algorithm for API rate limiting
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self):
        # In-memory storage (use Redis in production for distributed systems)
        self.buckets: Dict[str, Dict] = {}
        
        # Rate limits per tier (requests per minute)
        self.limits = {
            'free': {'per_minute': 10, 'per_month': 1000},
            'pro': {'per_minute': 100, 'per_month': 10000},
            'enterprise': {'per_minute': 1000, 'per_month': 100000}
        }
    
    def check_limit(self, key_id: str, tier: str = 'free', requests_count: int = 0, requests_limit: int = 1000) -> Dict:
        """
        Check if request is within rate limits
        
        Args:
            key_id: API key ID
            tier: Tier level
            requests_count: Current monthly request count
            requests_limit: Monthly request limit
        
        Returns:
            dict with 'allowed' boolean and rate limit info
        """
        now = datetime.utcnow()
        
        # Check monthly limit
        if requests_count >= requests_limit:
            return {
                'allowed': False,
                'reason': 'monthly_limit_exceeded',
                'limit': requests_limit,
                'remaining': 0,
                'reset_at': self._get_month_reset()
            }
        
        # Get or create bucket
        if key_id not in self.buckets:
            self.buckets[key_id] = {
                'tokens': self.limits[tier]['per_minute'],
                'last_refill': now
            }
        
        bucket = self.buckets[key_id]
        
        # Refill tokens based on time elapsed
        time_elapsed = (now - bucket['last_refill']).total_seconds()
        refill_rate = self.limits[tier]['per_minute'] / 60  # tokens per second
        tokens_to_add = time_elapsed * refill_rate
        
        bucket['tokens'] = min(
            self.limits[tier]['per_minute'],
            bucket['tokens'] + tokens_to_add
        )
        bucket['last_refill'] = now
        
        # Check if we have tokens available
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return {
                'allowed': True,
                'limit': self.limits[tier]['per_minute'],
                'remaining': int(bucket['tokens']),
                'reset_at': (now + timedelta(minutes=1)).isoformat()
            }
        else:
            return {
                'allowed': False,
                'reason': 'rate_limit_exceeded',
                'limit': self.limits[tier]['per_minute'],
                'remaining': 0,
                'reset_at': (now + timedelta(seconds=60)).isoformat(),
                'retry_after': 60
            }
    
    def _get_month_reset(self) -> str:
        """Get the first day of next month"""
        now = datetime.utcnow()
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)
        return next_month.isoformat()


# Singleton instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the rate limiter singleton"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
