#!/usr/bin/env python3
import google.generativeai as genai
import os

# Configure API key
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    print("GEMINI_API_KEY not found in environment variables")
    exit(1)

genai.configure(api_key=api_key)

# List available models
print("Available Gemini models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")