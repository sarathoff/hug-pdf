"""
API Key Management Service
Handles generation, validation, and lifecycle of API keys for developer access
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
from supabase import Client
import logging

logger = logging.getLogger(__name__)


class APIKeyService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    def generate_api_key(self, user_id: str, name: str, tier: str = "free") -> Dict:
        """
        Generate a new API key for a user
        
        Args:
            user_id: User's ID from Supabase auth
            name: Friendly name for the API key
            tier: Tier level (free, pro, enterprise)
        
        Returns:
            dict with api_key (plaintext, show once) and key details
        """
        try:
            # Generate secure random key
            key_suffix = secrets.token_urlsafe(32)
            prefix = "pdf_live" if tier != "test" else "pdf_test"
            api_key = f"{prefix}_{key_suffix}"
            
            # Hash the key for storage (never store plaintext)
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Store in database
            result = self.supabase.table('api_keys').insert({
                'user_id': user_id,
                'name': name,
                'key_hash': key_hash,
                'key_prefix': f"{prefix}_{key_suffix[:8]}...",  # For display
                'tier': tier,
                'is_active': True,
                'created_at': datetime.utcnow().isoformat(),
                'last_used_at': None,
                'requests_count': 0,
                'requests_limit': 1000 if tier == "free" else 10000
            }).execute()
            
            logger.info(f"Generated API key for user {user_id}: {name}")
            
            return {
                'success': True,
                'api_key': api_key,  # Show once, never again
                'key_id': result.data[0]['id'],
                'name': name,
                'tier': tier,
                'prefix': f"{prefix}_{key_suffix[:8]}..."
            }
            
        except Exception as e:
            logger.error(f"Failed to generate API key: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """
        Validate an API key and return key details
        
        Args:
            api_key: The API key to validate
        
        Returns:
            dict with key details if valid, None if invalid
        """
        try:
            # Hash the provided key
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            logger.info(f"Validating API key, hash: {key_hash}")
            
            # Look up in database
            result = self.supabase.table('api_keys').select('*').eq('key_hash', key_hash).eq('is_active', True).execute()
            
            if not result.data:
                logger.warning(f"No API key found in database for hash: {key_hash[:10]}...")
                return None
            
            key_data = result.data[0]
            
            # Check if key is active (though already filtered in query, extra safety/logging)
            if not key_data.get('is_active', False):
                logger.warning(f"API key '{key_data['name']}' ({key_data['id']}) is marked as inactive")
                return None
            
            # Check request limits
            if key_data['requests_count'] >= key_data['requests_limit']:
                logger.warning(f"API key '{key_data['name']}' has exceeded its request limit: {key_data['requests_count']}/{key_data['requests_limit']}")
                # We return it anyway, the rate limiter in server.py will handle the block
            
            logger.info(f"API key validated successfully: {key_data['name']} (User: {key_data['user_id']})")
            
            # Update last used timestamp
            self.supabase.table('api_keys').update({
                'last_used_at': datetime.utcnow().isoformat()
            }).eq('id', key_data['id']).execute()
            
            return {
                'id': key_data['id'],
                'user_id': key_data['user_id'],
                'name': key_data['name'],
                'tier': key_data['tier'],
                'requests_count': key_data['requests_count'],
                'requests_limit': key_data['requests_limit']
            }
            
        except Exception as e:
            logger.error(f"API key validation error: {e}", exc_info=True)
            return None
    
    def track_usage(self, key_id: str, endpoint: str, status_code: int) -> None:
        """Track API usage for analytics and rate limiting"""
        try:
            # Increment request count
            self.supabase.rpc('increment_api_key_requests', {'key_id': key_id}).execute()
            
            # Log usage
            self.supabase.table('api_usage').insert({
                'api_key_id': key_id,
                'endpoint': endpoint,
                'status_code': status_code,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
    
    def get_user_api_keys(self, user_id: str) -> list:
        """Get all API keys for a user"""
        try:
            result = self.supabase.table('api_keys').select('id, name, key_prefix, tier, is_active, created_at, last_used_at, requests_count, requests_limit').eq('user_id', user_id).order('created_at', desc=True).execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to get API keys: {e}")
            return []
    
    def revoke_api_key(self, key_id: str, user_id: str) -> bool:
        """Revoke an API key"""
        try:
            self.supabase.table('api_keys').update({
                'is_active': False
            }).eq('id', key_id).eq('user_id', user_id).execute()
            
            logger.info(f"Revoked API key {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke API key: {e}")
            return False


# Singleton instance
_api_key_service: Optional[APIKeyService] = None


def get_api_key_service(supabase_client: Client) -> APIKeyService:
    """Get or create the API key service singleton"""
    global _api_key_service
    if _api_key_service is None:
        _api_key_service = APIKeyService(supabase_client)
    return _api_key_service
