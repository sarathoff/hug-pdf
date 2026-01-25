import os
import logging
from typing import Dict, Optional
from firecrawl import FirecrawlApp
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class LinkedInService:
    def __init__(self):
        self.gemini_service = GeminiService() # Initialize Gemini Service
        api_key = os.environ.get('FIRECRAWL_API_KEY')
        if not api_key:
            logger.warning("FIRECRAWL_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = FirecrawlApp(api_key=api_key)
            logger.info("Firecrawl client initialized successfully")
    
    def scrape_linkedin_profile(self, linkedin_url: str) -> Optional[Dict]:
        """
        Scrape LinkedIn profile using Firecrawl (Markdown) and extract structured data using Gemini
        
        Args:
            linkedin_url: LinkedIn profile URL (e.g., https://www.linkedin.com/in/username)
            
        Returns:
            Dictionary containing structured profile data or None if scraping fails
        """
        if not self.client:
            logger.error("Firecrawl client not initialized - API key missing")
            return None
        
        # Validate LinkedIn URL
        if 'linkedin.com/in/' not in linkedin_url:
            logger.error(f"Invalid LinkedIn URL: {linkedin_url}")
            return None
        
        try:
            logger.info(f"Scraping LinkedIn profile: {linkedin_url}")
            
            # Define schema for structured data extraction
            schema = {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Full name of the person"},
                    "headline": {"type": "string", "description": "Professional headline or current title"},
                    "about": {"type": "string", "description": "About section or professional summary"},
                    "location": {"type": "string", "description": "Location"},
                    "experience": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Job title"},
                                "company": {"type": "string", "description": "Company name"},
                                "duration": {"type": "string", "description": "Duration of employment"},
                                "description": {"type": "string", "description": "Description of roles and responsibilities"}
                            }
                        }
                    },
                    "education": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "school": {"type": "string"},
                                "degree": {"type": "string"},
                                "field": {"type": "string"},
                                "date": {"type": "string"}
                            }
                        }
                    },
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["name"]
            }
            
            # Clean URL - remove trailing slash and ensure proper format
            clean_url = linkedin_url.rstrip('/')
            
            # STEP 1: Scrape raw markdown using Firecrawl
            logger.info(f"Step 1: Scraping raw markdown from {clean_url}")
            
            # Use Firecrawl scrape method with explicit keyword arguments
            # The v2 SDK expects arguments directly, not in a params dict
            
            try:
                # Try cleaner v2 scrape method directly
                scrape_result = self.client.scrape(
                    clean_url,
                    formats=['markdown']
                )
            except TypeError as e:
                # Fallback if params dict is expected (older versions)
                logger.warning(f"Standard scrape failed ({e}), trying with params dict...")
                try:
                    scrape_result = self.client.scrape(
                        clean_url,
                        params={'formats': ['markdown']}
                    )
                except AttributeError:
                     # Very old SDK
                     scrape_result = self.client.scrape_url(
                        clean_url,
                        params={'formats': ['markdown']}
                     )
            
            markdown_content = None
            if scrape_result:
                if isinstance(scrape_result, dict):
                    markdown_content = scrape_result.get('markdown')
                elif hasattr(scrape_result, 'markdown'):
                    markdown_content = scrape_result.markdown
            
            if not markdown_content:
                logger.error(f"Failed to retrieve markdown content. Result: {scrape_result}")
                # Fallback: check if 'data' or 'extract' has it
                if scrape_result and isinstance(scrape_result, dict) and 'data' in scrape_result:
                     return None # Structure mismatch
                return None
                
            logger.info(f"Retrieved {len(markdown_content)} chars of markdown")
            
            # STEP 2: Extract structured data using Gemini
            logger.info("Step 2: Extracting structured data using Gemini...")
            extracted_data = self.gemini_service.extract_json_from_markdown(markdown_content, schema)
            
            if extracted_data and 'name' in extracted_data:
                logger.info(f"Successfully extracted LinkedIn data for: {extracted_data.get('name', 'Unknown')}")
                return extracted_data
            else:
                logger.error("Failed to extract structured data from markdown")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping LinkedIn profile: {str(e)}")
            return None
    
    def validate_linkedin_url(self, url: str) -> bool:
        """Validate if URL is a valid LinkedIn profile URL"""
        return 'linkedin.com/in/' in url.lower()
