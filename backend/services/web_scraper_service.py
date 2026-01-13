import requests
from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)

class WebScraperService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_url(self, url: str) -> str:
        """
        Fetches and extracts clean text from a URL.
        """
        try:
            logger.info(f"Scraping URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                element.decompose()
                
            # Get text
            text = soup.get_text(separator=' ')
            
            # Clean text
            # specialized cleaning
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit length to avoid context window explosion (e.g. 15k chars per source)
            return text[:15000]
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            return ""
