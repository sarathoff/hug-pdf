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
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            print(f"Token verification error: {e}")
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
