import google.generativeai as genai
import os
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def generate_html_from_prompt(self, prompt: str) -> Dict[str, str]:
        """Generate complete HTML document from user prompt"""
        system_prompt = f"""
You are an expert HTML/CSS document generator. Create a beautiful, professional HTML document based on the user's request.

IMPORTANT REQUIREMENTS:
1. Generate COMPLETE HTML including <!DOCTYPE html>, <html>, <head>, and <body> tags
2. Use inline CSS within <style> tags in the <head>
3. Use 'DM Sans' font from Google Fonts throughout the document
4. Make it print-ready with proper page structure
5. Use professional styling with good typography and spacing
6. Add appropriate colors, borders, and layout for the document type
7. Structure the content logically with proper headings and sections
8. Ensure the HTML is valid and renders properly

User request: {prompt}

Generate ONLY the complete HTML code, nothing else. No explanations, no markdown code blocks, just the raw HTML.
"""
        
        try:
            response = self.model.generate_content(system_prompt)
            html_content = response.text.strip()
            
            # Clean up potential markdown formatting
            if html_content.startswith('```html'):
                html_content = html_content[7:]
            if html_content.startswith('```'):
                html_content = html_content[3:]
            if html_content.endswith('```'):
                html_content = html_content[:-3]
            
            html_content = html_content.strip()
            
            logger.info(f"Generated HTML document for prompt: {prompt[:50]}...")
            return {
                "html": html_content,
                "message": "I've generated your PDF content. You can see the preview on the right. Feel free to ask me to modify anything!"
            }
        except Exception as e:
            logger.error(f"Error generating HTML: {str(e)}")
            raise
    
    def modify_html(self, current_html: str, modification_request: str) -> Dict[str, str]:
        """Modify existing HTML based on user request"""
        system_prompt = f"""
You are an expert at modifying HTML/CSS documents. The user has an existing HTML document and wants to make changes.

Current HTML:
{current_html}

User's modification request: {modification_request}

IMPORTANT:
1. Return the COMPLETE modified HTML document
2. Keep the same overall structure but apply the requested changes
3. Maintain 'DM Sans' font unless specifically asked to change it
4. Ensure all changes are properly integrated
5. Keep it print-ready and professional

Generate ONLY the complete modified HTML code, nothing else. No explanations, no markdown code blocks, just the raw HTML.
"""
        
        try:
            response = self.model.generate_content(system_prompt)
            html_content = response.text.strip()
            
            # Clean up potential markdown formatting
            if html_content.startswith('```html'):
                html_content = html_content[7:]
            if html_content.startswith('```'):
                html_content = html_content[3:]
            if html_content.endswith('```'):
                html_content = html_content[:-3]
            
            html_content = html_content.strip()
            
            logger.info(f"Modified HTML based on request: {modification_request[:50]}...")
            return {
                "html": html_content,
                "message": "I've updated the document based on your request."
            }
        except Exception as e:
            logger.error(f"Error modifying HTML: {str(e)}")
            raise