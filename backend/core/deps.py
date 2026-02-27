from fastapi import Header, HTTPException
from typing import Optional
import logging
from services.auth_service import AuthService
from backend.core.config import settings
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Initialize Supabase clients (Singleton-ish)
supabase: Optional[Client] = None
supabase_admin: Optional[Client] = None

try:
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            supabase_admin = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Supabase Admin client initialized")
        else:
            logger.warning("SUPABASE_SERVICE_ROLE_KEY not found! Admin actions will fail.")
            supabase_admin = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
except Exception as e:
    logger.warning(f"Failed to initialize Supabase: {e}")

auth_service = AuthService()

async def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Get current user from JWT token using Supabase for persistence (Shared Dependency)"""
    if not authorization or not authorization.startswith('Bearer '):
        logger.debug("get_current_user: No Bearer token in Authorization header")
        return None
    
    token = authorization.replace('Bearer ', '')
    payload = auth_service.verify_token(token)
    if not payload:
        logger.warning("get_current_user: Token verification FAILED — check SUPABASE_JWT_SECRET env var")
        return None
        
    if not supabase:
        logger.error("get_current_user: Supabase client is None — check SUPABASE_URL and SUPABASE_KEY env vars")
        return None
        
    # Check DB
    response = supabase.table("users").select("*").eq("user_id", payload['user_id']).execute()
    
    # If user exists, return immediately
    if response.data and len(response.data) > 0:
        return response.data[0]
    
    # User doesn't exist, try to create
    try:
        if not supabase_admin:
            logger.warning("No admin client available to create user")
            return None
            
        new_user = {
            "user_id": payload['user_id'],
            "email": payload.get('email'),
            "credits": 3,
            "plan": "free"
        }
        res = supabase_admin.table("users").insert(new_user).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception as e:
        # Handle 409 Conflict (user already exists due to race condition)
        error_str = str(e)
        if '409' in error_str or 'conflict' in error_str.lower() or '23505' in error_str or 'duplicate key' in error_str.lower():
            # User was created by another request, fetch it
            logger.info("User already exists (race condition), fetching...")
            retry = supabase_admin.table("users").select("*").eq("user_id", payload['user_id']).execute()
            if retry.data and len(retry.data) > 0:
                return retry.data[0]
        logger.error(f"Failed to create user: {e}")
        return None
    
    logger.warning("User creation returned no data")
    return None

def get_supabase_client():
    return supabase

def get_supabase_admin():
    return supabase_admin
