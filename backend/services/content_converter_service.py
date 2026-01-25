import os
import logging
from typing import Dict, Optional
from firecrawl import FirecrawlApp
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ContentConverterService:
    """Universal web content converter supporting blogs, articles, websites, and more"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
        api_key = os.environ.get('FIRECRAWL_API_KEY')
        if not api_key:
            logger.warning("FIRECRAWL_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = FirecrawlApp(api_key=api_key)
            logger.info("Firecrawl client initialized successfully")
    
    def scrape_content(self, url: str) -> Optional[Dict]:
        """
        Scrape any web URL and return markdown content with metadata
        
        Args:
            url: Any valid web URL (blog, article, website, etc.)
            
        Returns:
            Dictionary containing markdown content and metadata or None if scraping fails
        """
        if not self.client:
            logger.error("Firecrawl client not initialized - API key missing")
            return None
        
        try:
            logger.info(f"Scraping content from: {url}")
            
            # Clean URL
            clean_url = url.rstrip('/')
            
            # Scrape raw markdown using Firecrawl
            scrape_result = self.client.scrape(
                clean_url,
                formats=['markdown']
            )
            
            markdown_content = None
            metadata = {}
            
            if scrape_result:
                if isinstance(scrape_result, dict):
                    markdown_content = scrape_result.get('markdown')
                    metadata = scrape_result.get('metadata', {})
                elif hasattr(scrape_result, 'markdown'):
                    markdown_content = scrape_result.markdown
                    if hasattr(scrape_result, 'metadata'):
                        # Convert metadata object to dict if needed
                        meta_obj = scrape_result.metadata
                        if isinstance(meta_obj, dict):
                            metadata = meta_obj
                        elif hasattr(meta_obj, '__dict__'):
                            metadata = vars(meta_obj)
                        else:
                            metadata = {}
            
            if not markdown_content:
                logger.error(f"Failed to retrieve markdown content. Result: {scrape_result}")
                return None
                
            logger.info(f"Retrieved {len(markdown_content)} chars of markdown")
            
            return {
                'markdown': markdown_content,
                'metadata': metadata,
                'url': url
            }
                
        except Exception as e:
            logger.error(f"Error scraping content: {str(e)}")
            return None
    
    def convert_to_pdf(self, url: str, conversion_type: str = 'article', options: Optional[Dict] = None) -> Optional[Dict]:
        """
        Convert web content to PDF-ready LaTeX
        
        Args:
            url: Web URL to convert
            conversion_type: Type of conversion (blog, article, website, resume, docs)
            options: Additional conversion options
            
        Returns:
            Dictionary with LaTeX content and metadata
        """
        if options is None:
            options = {}
        
        # Step 1: Scrape content
        content_data = self.scrape_content(url)
        if not content_data:
            return None
        
        markdown = content_data['markdown']
        metadata = content_data.get('metadata', {})
        
        # Step 2: Convert to LaTeX based on type
        logger.info(f"Converting to PDF format: {conversion_type}")
        
        try:
            latex_content = self.gemini_service.format_content_for_pdf(
                markdown=markdown,
                conversion_type=conversion_type,
                metadata=metadata,
                options=options
            )
            
            return {
                'latex': latex_content,
                'metadata': metadata,
                'url': url,
                'conversion_type': conversion_type,
                'message': f'Successfully converted {conversion_type} to PDF format'
            }
            
        except Exception as e:
            logger.error(f"Error converting to PDF: {str(e)}")
            return None
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is a valid web URL"""
        return url.startswith('http://') or url.startswith('https://')
