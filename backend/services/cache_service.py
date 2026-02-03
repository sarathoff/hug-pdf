from google import genai
from google.genai import types
import os
import logging
import hashlib
from typing import Optional, Dict
from datetime import datetime, timedelta
import json
from backend.core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    """Service for managing Gemini context caching to reduce token usage and costs"""
    
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        
        # In-memory cache metadata storage
        # In production, consider using Redis or database
        self.cache_metadata: Dict[str, dict] = {}
        
        # Cache statistics
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'tokens_saved': 0,
            'cost_saved': 0.0
        }
    
    def _generate_cache_key(self, mode: str, content_hash: Optional[str] = None, version: str = "v1") -> str:
        """Generate a unique cache key based on mode and content"""
        if content_hash:
            return f"{mode}_{version}_{content_hash}"
        return f"{mode}_{version}"
    
    def _hash_content(self, content: str) -> str:
        """Generate hash of content for cache key"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def create_cache(
        self, 
        cache_key: str,
        system_instruction: str,
        model: str = settings.GEMINI_MODEL_STARTER,
        ttl_seconds: int = 3600
    ) -> Optional[str]:
        """
        Create a cached content in Gemini
        
        Args:
            cache_key: Unique identifier for this cache
            system_instruction: The content to cache (system prompts, instructions, etc.)
            model: Gemini model name
            ttl_seconds: Time-to-live in seconds (default 1 hour)
        
        Returns:
            Cache name if successful, None otherwise
        """
        try:
            # Check if cache already exists and is valid
            if cache_key in self.cache_metadata:
                metadata = self.cache_metadata[cache_key]
                if datetime.fromisoformat(metadata['expires_at']) > datetime.now():
                    logger.info(f"Cache {cache_key} already exists and is valid")
                    return metadata['cache_name']
            
            # Create new cache using Gemini API
            # Updated for correct google-genai SDK usage
            # The SDK expects 'config' for contents in some versions, or direct arguments
            # We will use the standard pattern for v0.1+
            
            # Use a supported model for caching
            # gemini-2.0-flash-exp and gemini-1.5-flash both support caching
            # No fallback needed - use the model as provided
            
            # Construct the cache config
            # Note: create() signature depends on the exact SDK version.
            # Assuming google-genai 0.2+ or 0.3+
            
            from google.genai import types

            cache_response = self.client.caches.create(
                model=model,
                config=types.CreateCacheConfig(
                    contents=[
                        types.Content(
                            parts=[types.Part(text=system_instruction)]
                        )
                    ],
                    ttl=f"{ttl_seconds}s",
                    display_name=cache_key
                )
            )
            
            cache_name = cache_response.name
            
            # Store metadata
            self.cache_metadata[cache_key] = {
                'cache_name': cache_name,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat(),
                'token_count': len(system_instruction.split()),  # Rough estimate
                'hit_count': 0,
                'model': model
            }
            
            logger.info(f"Created cache {cache_key} with name {cache_name}, TTL: {ttl_seconds}s")
            return cache_name
            
        except Exception as e:
            logger.error(f"Failed to create cache {cache_key}: {str(e)}")
            # Fallback: if cache creation fails, just return None so we proceed without cache
            return None
    
    def get_cache(self, cache_key: str) -> Optional[str]:
        """
        Get cache name if it exists and is valid
        
        Returns:
            Cache name if valid, None if expired or doesn't exist
        """
        if cache_key not in self.cache_metadata:
            self.stats['cache_misses'] += 1
            return None
        
        metadata = self.cache_metadata[cache_key]
        
        # Check if cache has expired
        if datetime.fromisoformat(metadata['expires_at']) <= datetime.now():
            logger.info(f"Cache {cache_key} has expired")
            self.stats['cache_misses'] += 1
            del self.cache_metadata[cache_key]
            return None
        
        # Update hit count
        metadata['hit_count'] += 1
        self.stats['cache_hits'] += 1
        
        # Estimate tokens saved (rough calculation)
        tokens_saved = metadata['token_count']
        self.stats['tokens_saved'] += tokens_saved
        
        # Estimate cost saved (cached tokens are ~90% cheaper)
        # Gemini Flash: $0.00015 per 1K tokens input, cached: $0.000015 per 1K tokens
        cost_saved = (tokens_saved / 1000) * (0.00015 - 0.000015)
        self.stats['cost_saved'] += cost_saved
        
        logger.info(f"Cache hit for {cache_key}, tokens saved: {tokens_saved}, cost saved: ${cost_saved:.6f}")
        return metadata['cache_name']
    
    def invalidate_cache(self, cache_key: str) -> bool:
        """Invalidate a specific cache"""
        if cache_key in self.cache_metadata:
            try:
                cache_name = self.cache_metadata[cache_key]['cache_name']
                # Delete from Gemini (if API supports it)
                # self.client.caches.delete(cache_name)
                del self.cache_metadata[cache_key]
                logger.info(f"Invalidated cache {cache_key}")
                return True
            except Exception as e:
                logger.error(f"Failed to invalidate cache {cache_key}: {str(e)}")
                return False
        return False
    
    def get_or_create_cache(
        self,
        cache_key: str,
        system_instruction: str,
        model: str = settings.GEMINI_MODEL_STARTER,
        ttl_seconds: int = 3600
    ) -> Optional[str]:
        """
        Get existing cache or create new one if it doesn't exist
        
        This is the main method to use in your services
        """
        # Try to get existing cache
        cache_name = self.get_cache(cache_key)
        
        if cache_name:
            return cache_name
        
        # Create new cache if it doesn't exist
        return self.create_cache(cache_key, system_instruction, model, ttl_seconds)
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_rate = (self.stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'hit_rate_percent': round(hit_rate, 2),
            'tokens_saved': self.stats['tokens_saved'],
            'cost_saved_usd': round(self.stats['cost_saved'], 6),
            'active_caches': len(self.cache_metadata)
        }
    
    def cleanup_expired_caches(self):
        """Remove expired caches from metadata"""
        now = datetime.now()
        expired_keys = [
            key for key, metadata in self.cache_metadata.items()
            if datetime.fromisoformat(metadata['expires_at']) <= now
        ]
        
        for key in expired_keys:
            del self.cache_metadata[key]
            logger.info(f"Cleaned up expired cache {key}")
        
        return len(expired_keys)
