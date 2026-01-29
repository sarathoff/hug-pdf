from google import genai
from google.genai import types
import os
from typing import Dict, Optional
import logging
import json
from services.perplexity_service import PerplexityService
from services.web_scraper_service import WebScraperService
from services.pexels_service import PexelsService
from services.cache_service import CacheService

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        self.perplexity_service = PerplexityService()
        self.web_scraper = WebScraperService()
        self.pexels_service = PexelsService()
        self.cache_service = CacheService()
        self.CACHE_VERSION = "v1"  # Increment when changing prompts
    
    def generate_resume_from_linkedin(self, linkedin_data: Dict) -> Dict[str, str]:
        """Generate professional resume LaTeX from LinkedIn profile data
        
        Args:
            linkedin_data: Dictionary containing LinkedIn profile data (name, experience, education, etc.)
            
        Returns:
            Dictionary with 'html', 'latex', and 'message' keys
        """
        # Format LinkedIn data for the prompt
        linkedin_json = json.dumps(linkedin_data, indent=2)
        
        system_prompt = f"""
You are an expert resume writer. Create a professional, ATS-friendly resume in LaTeX format based on the LinkedIn profile data provided.

LINKEDIN PROFILE DATA:
{linkedin_json}

RESUME REQUIREMENTS:
1. Use \\documentclass{{article}} with clean, professional formatting
2. Include these sections (if data available):
   - Header with name, contact info (email, phone if available, LinkedIn URL)
   - Professional Summary/Headline
   - Work Experience (reverse chronological order)
   - Education (reverse chronological order)
   - Skills
   - Certifications (if available)
3. Format work experience with:
   - Job title and company name
   - Duration (dates)
   - Location (if available)
   - Bullet points for responsibilities/achievements
4. Use professional LaTeX packages:
   - \\usepackage[left=0.75in,top=0.6in,right=0.75in,bottom=0.6in]{{geometry}}
   - \\usepackage{{hyperref}} for clickable links
   - \\usepackage{{enumitem}} for better lists
   - \\usepackage{{lmodern}} for fonts
5. Keep it to 1-2 pages maximum
6. Use clean, readable fonts
7. Professional spacing and layout
8. Make it ATS-friendly (no complex tables, clear section headers)

STYLE GUIDELINES:
- Use \\textbf{{}} for emphasis
- Use \\section*{{}} for main sections (no numbering)
- Use itemize environment for bullet points
- Keep descriptions concise and achievement-focused
- Use action verbs for experience descriptions
- Format dates consistently

Generate ONLY the complete LaTeX code, nothing else. No explanations, no markdown code blocks.
"""
        
        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL_STARTER,
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
            
            logger.info(f"Generated resume for: {linkedin_data.get('name', 'Unknown')}")
            
            return {
                "html": latex_content,
                "latex": latex_content,
                "message": f"I've created a professional resume for {linkedin_data.get('name', 'you')} based on the LinkedIn profile!",
                "mode": "normal"
            }
        except Exception as e:
            logger.error(f"Error generating resume from LinkedIn data: {str(e)}")
            raise
