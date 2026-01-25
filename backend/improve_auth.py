# Improve verify_token to handle Base64 encoded secrets

from services.auth_service import AuthService
import inspect

with open('services/auth_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to import base64
if 'import base64' not in content:
    content = content.replace('import jwt', 'import jwt\nimport base64')

# Update verify_supabase_token to try Base64 decoding
# We'll replace the first try/except block start
old_logic = '''            # Verify the token
            payload = jwt.decode(
                token,
                supabase_jwt_secret,
                algorithms=['HS256'],
                options={"verify_aud": False}  # Supabase tokens don't always have aud
            )'''

new_logic = '''            # Verify the token
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
                    raise # Re-raise original or let it fall through to JWKS'''

content = content.replace(old_logic, new_logic)

with open('services/auth_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated auth_service.py to try Base64 decoded secret!")
