import logging
import jwt
import base64
from datetime import datetime, timedelta
import os
from typing import Optional
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    logger.warning("SECURITY WARNING: JWT_SECRET not set in environment. Generating a random secret. Existing sessions will be invalidated on restart.")
    import secrets
    JWT_SECRET = secrets.token_urlsafe(32)

JWT_ALGORITHM = 'HS256'

class AuthService:
    @staticmethod
    def verify_supabase_token(token: str) -> Optional[dict]:
        """Verify Supabase JWT token"""
        try:
            # Supabase tokens are signed with the JWT_SECRET from your Supabase project
            # For production, you should fetch the public key from Supabase
            supabase_jwt_secret = os.environ.get('SUPABASE_JWT_SECRET', JWT_SECRET)
            print(f"DEBUG: Verifying token with secret ending in ...{supabase_jwt_secret[-6:] if supabase_jwt_secret else 'NONE'}")
            
            # Decode without verification first to get the header
            unverified_header = jwt.get_unverified_header(token)
            print(f"DEBUG: Token Header: {unverified_header}")
            
            # Decode without verification first to get the header
            unverified = jwt.decode(token, options={"verify_signature": False})
            
            # Verify the token
            try:
                # Try standard string secret first
                payload = jwt.decode(
                    token,
                    supabase_jwt_secret,
                    algorithms=['HS256'],
                    options={"verify_aud": False}
                )
            except jwt.InvalidSignatureError:
                # If signature fails, try decoding the secret from Base64
                # Supabase secrets are often Base64 encoded
                try:
                    logger.info("DEBUG: Standard verification failed, trying Base64 decoded secret...")
                    decoded_secret = base64.urlsafe_b64decode(supabase_jwt_secret + "==") # Ensure padding
                    payload = jwt.decode(
                        token,
                        decoded_secret,
                        algorithms=['HS256'],
                        options={"verify_aud": False}
                    )
                    logger.info("DEBUG: Verification successful with Base64 decoded secret!")
                except Exception as b64_error:
                    logger.info(f"DEBUG: Base64 verification also failed: {b64_error}")
                    raise # Re-raise original or let it fall through to JWKS
            
            # Extract user_id from Supabase token structure
            logging.info(f"DEBUG: Token verified successfully. Payload: {payload}")
            
            user_id = payload.get('sub')  # Supabase uses 'sub' for user ID
            email = payload.get('email')
            
            if not user_id:
                logging.error("DEBUG: Token valid but 'sub' (user_id) is MISSING in payload")
                return None
                
            return {
                'user_id': user_id,
                'email': email,
                'exp': payload.get('exp')
            }
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            # If standard HS256 failed, check if we should try JWKS (for ES256/RS256)
            try:
                unverified_header = jwt.get_unverified_header(token)
                alg = unverified_header.get('alg')
                
                if alg in ['RS256', 'ES256']:
                    print(f"DEBUG: Token uses {alg}, attempting JWKS verification...")
                    supabase_url = os.environ.get("SUPABASE_URL")
                    if not supabase_url:
                        print("DEBUG: SUPABASE_URL missing, cannot fetch JWKS")
                        return None
                        
                    jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
                    jwks_client = jwt.PyJWKClient(jwks_url)
                    signing_key = jwks_client.get_signing_key_from_jwt(token)
                    
                    payload = jwt.decode(
                        token,
                        signing_key.key,
                        algorithms=[alg],
                        options={"verify_aud": False}
                    )
                    
                    # Extract user_id
                    user_id = payload.get('sub')
                    email = payload.get('email')
                    
                    if not user_id:
                        return None
                        
                    return {
                        'user_id': user_id,
                        'email': email,
                        'exp': payload.get('exp')
                    }
            except Exception as jwks_error:
                print(f"DEBUG: JWKS verification failed: {jwks_error}")
            
            # Original error reporting if JWKS didn't succeed
            print(f"DEBUG: Token verification failed: {e}")
            return None
        except Exception as e:
            print(f"DEBUG: Token verification error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify JWT token (supports both custom and Supabase tokens)"""
        # Try Supabase token first
        result = AuthService.verify_supabase_token(token)
        if result:
            return result
            
        # Fallback to custom JWT for backward compatibility
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except:
            return None
