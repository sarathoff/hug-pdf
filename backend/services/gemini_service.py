from google import genai
from google.genai import types
import os
from typing import Dict
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

logger = logging.getLogger(__name__)

def is_retryable_error(exception):
    """Check if the exception is a 503 Service Unavailable or Overloaded error"""
    error_str = str(exception)
    return "503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower()

class GeminiService:
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception(is_retryable_error),
        reraise=True
    )
    def generate_latex_from_prompt(self, prompt: str) -> str:
        """Generate LaTeX document from user prompt"""
        system_prompt = f"""
You are an expert LaTeX document generator. Create a beautiful, professional LaTeX document based on the user's request.

IMPORTANT REQUIREMENTS:
1. Generate COMPLETE LaTeX code starting with \\documentclass
2. Use appropriate document class (article, report, etc.)
3. Include necessary packages (geometry, fontenc, inputenc, etc.)
4. Use professional formatting with proper sections and structure
5. Set appropriate margins and page layout
6. Use clean, readable typography
7. Structure content logically

User request: {prompt}

Generate ONLY the complete LaTeX code, nothing else. No explanations, no markdown code blocks, just the raw LaTeX.
"""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=system_prompt
            )
            latex_content = response.text.strip()

            # Clean up potential markdown formatting
            if latex_content.startswith('```latex') or latex_content.startswith('```tex'):
                latex_content = latex_content.split('\n', 1)[1] if '\n' in latex_content else latex_content[7:]
            if latex_content.startswith('```'):
                latex_content = latex_content[3:]
            if latex_content.endswith('```'):
                latex_content = latex_content[:-3]

            latex_content = latex_content.strip()

            logger.info(f"Generated LaTeX document for prompt: {prompt[:50]}...")
            return latex_content
        except Exception as e:
            # Logging is handled by the retry decorator or the caller if all retries fail
            # We just re-raise here to let tenacity handle it
            # But we can log the specific 503 if we want
            if is_retryable_error(e):
                logger.warning(f"Gemini API overloaded (503), retrying... Error: {str(e)}")
            else:
                logger.error(f"Error generating LaTeX: {str(e)}")
            raise

    def generate_html_from_prompt(self, prompt: str) -> Dict[str, str]:
        """Generate LaTeX document from user prompt"""
        latex_content = self.generate_latex_from_prompt(prompt)

        logger.info(f"Generated LaTeX for prompt: {prompt[:50]}...")
        return {
            "html": latex_content,  # Send LaTeX as 'html' for backward compatibility
            "latex": latex_content,
            "message": "I've generated your document in LaTeX. You can see the code on the right. Feel free to ask me to modify anything!"
        }

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception(is_retryable_error),
        reraise=True
    )
    def modify_latex(self, current_latex: str, modification_request: str) -> str:
        """Modify existing LaTeX based on user request"""
        system_prompt = f"""
You are an expert at modifying LaTeX documents. The user has an existing LaTeX document and wants to make changes.

Current LaTeX:
{current_latex}

User's modification request: {modification_request}

IMPORTANT:
1. Return the COMPLETE modified LaTeX document
2. Keep the same overall structure but apply the requested changes
3. Ensure all changes are properly integrated
4. Keep it professional and well-formatted

Generate ONLY the complete modified LaTeX code, nothing else. No explanations, no markdown code blocks, just the raw LaTeX.
"""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=system_prompt
            )
            latex_content = response.text.strip()

            # Clean up potential markdown formatting
            if latex_content.startswith('```latex') or latex_content.startswith('```tex'):
                latex_content = latex_content.split('\n', 1)[1] if '\n' in latex_content else latex_content[7:]
            if latex_content.startswith('```'):
                latex_content = latex_content[3:]
            if latex_content.endswith('```'):
                latex_content = latex_content[:-3]

            latex_content = latex_content.strip()

            logger.info(f"Modified LaTeX based on request: {modification_request[:50]}...")
            return latex_content
        except Exception as e:
            if is_retryable_error(e):
                logger.warning(f"Gemini API overloaded (503), retrying... Error: {str(e)}")
            else:
                logger.error(f"Error modifying LaTeX: {str(e)}")
            raise

    def modify_html(self, current_html: str, modification_request: str, current_latex: str = None) -> Dict[str, str]:
        """Modify existing LaTeX based on user request"""
        # Use current_latex if provided, otherwise use current_html (which is actually LaTeX)
        latex_to_modify = current_latex if current_latex else current_html

        latex_content = self.modify_latex(latex_to_modify, modification_request)

        result = {
            "html": latex_content,  # Send LaTeX as 'html' for backward compatibility
            "latex": latex_content,
            "message": "I've updated the document based on your request."
        }

        logger.info(f"Modified LaTeX based on request: {modification_request[:50]}...")
        return result