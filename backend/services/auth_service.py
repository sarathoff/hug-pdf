import jwt
from datetime import datetime, timedelta
import os
from typing import Optional
import requests

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')
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
            payload = jwt.decode(
                token,
                supabase_jwt_secret,
                algorithms=['HS256'],
                options={"verify_aud": False}  # Supabase tokens don't always have aud
            )
            
            # Extract user_id from Supabase token structure
            user_id = payload.get('sub')  # Supabase uses 'sub' for user ID
            email = payload.get('email')
            
            if not user_id:
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
