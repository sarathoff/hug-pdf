"""
API Testing Script
Test the API key generation and PDF generation endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"

# Step 1: You need to get your user auth token first
# Login through your frontend and copy the token from browser DevTools
# Or use your existing login endpoint

USER_TOKEN = "YOUR_USER_TOKEN_HERE"  # Replace with actual token

def test_create_api_key():
    """Test creating an API key"""
    print("\n=== Testing API Key Creation ===")
    
    response = requests.post(
        f"{BASE_URL}/v1/keys",
        headers={
            "Authorization": f"Bearer {USER_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "name": "Test API Key",
            "tier": "free"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        api_key = response.json().get('api_key')
        print(f"\n✅ API Key created: {api_key}")
        print("⚠️  SAVE THIS KEY - it won't be shown again!")
        return api_key
    else:
        print(f"❌ Failed to create API key")
        return None


def test_list_api_keys():
    """Test listing API keys"""
    print("\n=== Testing List API Keys ===")
    
    response = requests.get(
        f"{BASE_URL}/v1/keys",
        headers={"Authorization": f"Bearer {USER_TOKEN}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_generate_pdf(api_key):
    """Test PDF generation"""
    print("\n=== Testing PDF Generation ===")
    
    response = requests.post(
        f"{BASE_URL}/v1/generate",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "prompt": "Create a simple invoice for ABC Company for $1000",
            "mode": "normal"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        # Save PDF
        with open("test_invoice.pdf", "wb") as f:
            f.write(response.content)
        print("✅ PDF generated successfully: test_invoice.pdf")
        print(f"Rate Limit - Remaining: {response.headers.get('X-RateLimit-Remaining')}")
    else:
        print(f"❌ Failed: {response.text}")


def test_rate_limiting(api_key):
    """Test rate limiting by making multiple requests"""
    print("\n=== Testing Rate Limiting ===")
    
    for i in range(12):
        response = requests.post(
            f"{BASE_URL}/v1/generate",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={"prompt": f"Test document {i+1}"}
        )
        
        remaining = response.headers.get('X-RateLimit-Remaining', 'N/A')
        print(f"Request {i+1}: Status {response.status_code}, Remaining: {remaining}")
        
        if response.status_code == 429:
            print(f"✅ Rate limit triggered at request {i+1}")
            print(f"Response: {response.json()}")
            break


if __name__ == "__main__":
    print("🚀 Starting API Tests")
    print("=" * 50)
    
    # Test 1: Create API key
    api_key = test_create_api_key()
    
    if not api_key:
        print("\n❌ Cannot proceed without API key")
        print("Please set USER_TOKEN in the script first")
        exit(1)
    
    # Test 2: List API keys
    test_list_api_keys()
    
    # Test 3: Generate PDF
    test_generate_pdf(api_key)
    
    # Test 4: Rate limiting
    # test_rate_limiting(api_key)  # Uncomment to test rate limits
    
    print("\n" + "=" * 50)
    print("✅ Tests completed!")
