import requests
import os
import json
from pathlib import Path

# Try to load .env manually
env_path = Path("d:/pdf/.env")
api_key = None
if env_path.exists():
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not api_key:
    api_key = os.environ.get('GEMINI_API_KEY')

if not api_key:
    print("GEMINI_API_KEY not found in .env or environment")
    exit(1)

# Mask the API key for printing
masked_key = api_key[:5] + "..." + api_key[-5:]
print(f"Using API Key: {masked_key}")

def check_models(version):
    print(f"\n--- Checking API Version: {version} ---")
    url = f"https://generativelanguage.googleapis.com/{version}/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"Found {len(models)} models.")
            for model in models:
                print(f"M: {model['name']}")
        else:
            print(f"Error {response.status_code}")
    except Exception as e:
        print(f"Failed to call {version}: {e}")

check_models("v1")
check_models("v1beta")

print("\n--- Testing specific model: gemini-1.5-flash ---")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
payload = {"contents": [{"parts": [{"text": "Say hello"}]}]}
response = requests.post(url, json=payload)
print(f"gemini-1.5-flash (v1beta) status: {response.status_code}")
if response.status_code != 200:
    print(response.text)

url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
response = requests.post(url, json=payload)
print(f"gemini-1.5-flash (v1) status: {response.status_code}")
if response.status_code != 200:
    print(response.text)
