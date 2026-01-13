import os
import logging
import requests
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class PerplexityService:
    """Service for integrating Perplexity API for research mode with citations"""
    
    def __init__(self):
        self.api_key = os.environ.get('PERPLEXITY_API_KEY')
        if not self.api_key:
            logger.warning("PERPLEXITY_API_KEY not found in environment variables")
        self.base_url = 'https://api.perplexity.ai'
        
    def research_query(self, query: str) -> Optional[Dict]:
        """
        Use Perplexity API to research a topic and return results with citations
        
        Args:
            query: The research query/topic
            
        Returns:
            Dict with 'content' (researched text) and 'citations' (list of sources)
        """
        if not self.api_key:
            logger.error("Perplexity API key not configured")
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'sonar',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a research assistant. Provide comprehensive, well-researched information with accurate citations.'
                    },
                    {
                        'role': 'user',
                        'content': query
                    }
                ],
                'return_citations': True,
                'return_images': False
            }
            
            response = requests.post(
                f'{self.base_url}/chat/completions',
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract content and citations
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                citations = data.get('citations', [])
                
                logger.info(f"Perplexity research completed with {len(citations)} citations")
                
                return {
                    'content': content,
                    'citations': citations
                }
            else:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Perplexity API: {str(e)}")
            return None
    
    def format_citations_for_latex(self, citations: List[str]) -> str:
        """
        Format citations as LaTeX bibliography entries
        
        Args:
            citations: List of citation URLs/sources
            
        Returns:
            LaTeX formatted bibliography section
        """
        if not citations:
            return ""
        
        latex_bib = "\\section*{References}\n\\begin{enumerate}\n"
        
        for i, citation in enumerate(citations, 1):
            # Clean up citation URL
            citation_text = citation.strip()
            latex_bib += f"  \\item {citation_text}\n"
        
        latex_bib += "\\end{enumerate}\n"
        
        return latex_bib
