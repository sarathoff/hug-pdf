#!/usr/bin/env python3
"""Test Gemini API directly"""
import os
import sys
sys.path.insert(0, 'd:/projects/pdf')

# Load environment
from dotenv import load_dotenv
load_dotenv('d:/projects/pdf/backend/services/.env')

from google import genai

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key loaded: {api_key[:10]}..." if api_key else "NO API KEY!")

try:
    client = genai.Client(api_key=api_key)
    
    print("\nTesting gemini-2.0-flash-exp...")
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents="Generate a simple LaTeX document with title 'Test'"
    )
    
    print(f"Success! Response length: {len(response.text)}")
    print(f"First 200 chars:\n{response.text[:200]}")
    
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
