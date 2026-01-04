from google import genai
import os

api_key = os.environ.get('GEMINI_API_KEY') or "AIzaSyDAglmQGxquZ8nKTonNcbu" 

client = genai.Client(api_key=api_key)

print("Available models:")
for model in client.models.list():
    print(f"- {model.name}")
