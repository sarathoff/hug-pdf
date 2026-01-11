from google import genai
from google.genai import types
import os
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        
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
6. Structure content logically

CRITICAL FONT & PACKAGE INSTRUCTIONS (TO PREVENT ERRORS):
1. USE ONLY STANDARD FONTS: Use \\usepackage{{lmodern}} or \\usepackage{{mathptmx}}. 
2. DO NOT use 'beramono', 'fvm', 'libertine', 'newtxmath', or 'pxfonts'. These cause compilation errors on many systems.
3. DO NOT use 'amssymb' if you are using a font package that already defines math symbols (like mathptmx).
4. If in doubt, stick to default Computer Modern or Latin Modern (lmodern).
5. Ensure all environments (begin/end) are properly closed.

SPACING & LAYOUT QUALITY INSTRUCTIONS (CRITICAL TO PREVENT OVERLAPPING):
1. ALWAYS use proper spacing between sections: \\vspace{{0.5em}} or \\medskip
2. For resumes/CVs: Use \\section*{{}} for main sections with \\vspace{{-0.5em}} after if needed
3. Avoid tight spacing - ensure adequate whitespace between elements
4. Use \\par or blank lines between paragraphs
5. For lists: Use proper itemize/enumerate environments with appropriate spacing
6. For headers with dates: Use \\hfill or tabular to prevent overlap
7. Set reasonable margins: \\usepackage[margin=0.75in]{{geometry}}
8. Use \\setlength{{\\parskip}}{{0.5em}} for paragraph spacing
9. Avoid negative vspace unless absolutely necessary
10. Test layout: ensure no text overlaps by using proper LaTeX structures

IMAGE HANDLING INSTRUCTIONS:
1. ALWAYS include \\usepackage{{graphicx}} in the preamble if images are mentioned
2. When user provides an image URL (in brackets like [URL: ...]), use \\includegraphics{{URL}}
3. Use appropriate width: \\includegraphics[width=0.5\\textwidth]{{URL}}
4. Center images: \\begin{{center}} ... \\end{{center}}
5. Add captions if appropriate: \\begin{{figure}}[h] \\centering \\includegraphics... \\caption{{...}} \\end{{figure}}

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

CRITICAL FONT & PACKAGE INSTRUCTIONS:
1. If the user asks to fix fonts/errors: REMOVE 'beramono', 'libertine', 'newtxmath'. REPLACE with \\usepackage{{lmodern}}.
2. Ensure no conflicting packages (e.g. amssymb vs newtxmath).
3. Stick to standard, safe LaTeX packages.

SPACING & LAYOUT QUALITY INSTRUCTIONS (PREVENT OVERLAPPING):
1. Maintain proper spacing between sections: \\vspace{{0.5em}} or \\medskip
2. Ensure adequate whitespace between elements
3. Use \\hfill or tabular for headers with dates to prevent overlap
4. Avoid negative vspace unless necessary
5. Keep reasonable margins and paragraph spacing

IMAGE HANDLING INSTRUCTIONS:
1. If adding images, ALWAYS include \\usepackage{{graphicx}} in the preamble
2. When user provides an image URL (in brackets like [URL: ...]), use \\includegraphics{{URL}}
3. Use appropriate width: \\includegraphics[width=0.5\\textwidth]{{URL}}
4. Center images: \\begin{{center}} ... \\end{{center}}
5. Add captions if appropriate: \\begin{{figure}}[h] \\centering \\includegraphics... \\caption{{...}} \\end{{figure}}

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