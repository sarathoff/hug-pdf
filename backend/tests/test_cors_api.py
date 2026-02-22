import requests
import json
import sys

def test_cors():
    url = "http://localhost:8000/api/" # Adjust if backend is on a different port
    origin = "https://external-developer-app.com"
    
    print(f"Testing CORS on {url} with Origin: {origin}")
    
    try:
        # Simulate an OPTIONS preflight request
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization, Content-Type"
        }
        
        response = requests.options(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print("Headers:")
        for key, value in response.headers.items():
            if "access-control" in key.lower():
                print(f"  {key}: {value}")
        
        allow_origin = response.headers.get("Access-Control-Allow-Origin")
        if allow_origin == "*" or allow_origin == origin:
            print("\n✅ SUCCESS: CORS policy allows cross-origin requests.")
        else:
            print("\n❌ FAILURE: CORS policy does not allow cross-origin requests.")
            
    except Exception as e:
        print(f"\n❌ ERROR: Could not connect to backend. Is it running? {e}")

if __name__ == "__main__":
    test_cors()
