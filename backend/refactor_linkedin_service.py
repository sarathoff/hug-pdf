# Refactor LinkedInService to use markdown scraping + Gemini extraction

from services.linkedin_service import LinkedInService
from services.gemini_service import GeminiService
import inspect

# Read the file
with open('services/linkedin_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
new_imports = '''import os
import logging
from typing import Dict, Optional
from firecrawl import FirecrawlApp
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)'''

content = content.replace("import os\nimport logging\nfrom typing import Dict, Optional\nfrom firecrawl import FirecrawlApp\n\nlogger = logging.getLogger(__name__)", new_imports)

# 2. Update __init__ to include GeminiService
init_replacement = '''    def __init__(self):
        api_key = os.environ.get('FIRECRAWL_API_KEY')
        self.gemini_service = GeminiService()
        if not api_key:
            logger.warning("FIRECRAWL_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = FirecrawlApp(api_key=api_key)
            logger.info("Firecrawl client initialized successfully")'''

content = content.replace(
    '''    def __init__(self):
        api_key = os.environ.get('FIRECRAWL_API_KEY')
        if not api_key:
            logger.warning("FIRECRAWL_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = FirecrawlApp(api_key=api_key)
            logger.info("Firecrawl client initialized successfully")''', 
    init_replacement
)

# 3. Replace scrape_linkedin_profile logic
# We'll just replace the whole method body after schema definition

method_start_marker = "            # Define schema for structured data extraction"
# Find where the existing method logic starts and end
# Easier to just replace the whole file content for the method part using a big string replacement

new_method_logic = '''            # Define schema for structured data extraction
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
            scrape_result = self.client.scrape_url(
                clean_url,
                params={'formats': ['markdown']}
            )
            
            markdown_content = scrape_result.get('markdown') if scrape_result else None
            
            if not markdown_content:
                logger.error("Failed to retrieve markdown content from Firecrawl")
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
            return None'''

# We need to find the start and end of the try block in the original file
# It starts at line 40 in the previous filtered view
# We'll use a regex replacement or just string replacement if we can match the block

# Let's try to overwrite the whole file with the correct content structure
final_content = '''import os
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
            
            # Use scrape_url which returns markdown by default or specified format
            # Note: Checking API method vs SDK version. 
            # If scrape_url is not available (as seen in previous errors), we use scrape method
            
            try:
                # Try scrape_url first (older SDK)
                scrape_result = self.client.scrape_url(
                    clean_url,
                    params={'formats': ['markdown']}
                )
            except AttributeError:
                # Fallback to newer SDK 'scrape' method
                scrape_result = self.client.scrape(
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
'''

with open('services/linkedin_service.py', 'w', encoding='utf-8') as f:
    f.write(final_content)

print("Refactored LinkedInService to use Markdown + Gemini pipeline!")
