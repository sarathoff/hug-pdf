"""
Direct API Test Script - Bypasses Authentication
This script manually inserts an API key into the database for testing
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from supabase import create_client
import hashlib
import secrets

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    print("\nSet them in your environment or .env file")
    exit(1)

# Initialize Supabase with service role key (bypasses RLS)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def create_test_api_key(user_id: str = "test-user-123"):
    """Create a test API key directly in the database"""
    
    # Generate API key
    key_suffix = secrets.token_urlsafe(32)
    api_key = f"pdf_test_{key_suffix}"
    
    # Hash it
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Insert into database
    try:
        result = supabase.table('api_keys').insert({
            'user_id': user_id,  # This can be any UUID
            'name': 'Test API Key',
            'key_hash': key_hash,
            'key_prefix': f"pdf_test_{key_suffix[:8]}...",
            'tier': 'free',
            'is_active': True,
            'requests_count': 0,
            'requests_limit': 1000
        }).execute()
        
        print("✅ Test API Key created successfully!")
        print(f"\n🔑 API Key: {api_key}")
        print(f"\n⚠️  SAVE THIS KEY - it won't be shown again!")
        print(f"\nKey ID: {result.data[0]['id']}")
        print(f"User ID: {user_id}")
        
        return api_key
        
    except Exception as e:
        print(f"❌ Error creating API key: {e}")
        return None


def test_pdf_generation(api_key: str):
    """Test PDF generation with the API key"""
    import requests
    
    print("\n" + "="*50)
    print("Testing PDF Generation...")
    print("="*50)
    
    response = requests.post(
        "http://localhost:8000/api/v1/generate",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "prompt": "Create a simple invoice for ABC Company for $1000",
            "mode": "normal"
        }
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        with open("test_invoice.pdf", "wb") as f:
            f.write(response.content)
        print("\n✅ PDF generated successfully!")
        print("📄 Saved as: test_invoice.pdf")
        print(f"\n📊 Rate Limit Info:")
        print(f"  - Limit: {response.headers.get('X-RateLimit-Limit')}")
        print(f"  - Remaining: {response.headers.get('X-RateLimit-Remaining')}")
    else:
        print(f"\n❌ Failed: {response.text}")


if __name__ == "__main__":
    print("🚀 Direct API Test Script")
    print("="*50)
    
    # Create test API key
    api_key = create_test_api_key()
    
    if api_key:
        # Test PDF generation
        test_pdf_generation(api_key)
        
        print("\n" + "="*50)
        print("✅ Test completed!")
        print("\nYou can now use this API key for testing:")
        print(f"  {api_key}")
    else:
        print("\n❌ Failed to create test API key")
