import os
import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RephrasyService:
    """Service for integrating Rephrasy API for AI detection and content humanization"""
    
    def __init__(self):
        self.api_key = os.environ.get('REPHRASY_API_KEY')
        if not self.api_key:
            logger.warning("REPHRASY_API_KEY not found in environment variables during initialization")
            # Try reloading dotenv as a fallback
            try:
                from dotenv import load_dotenv
                from pathlib import Path
                
                # Verify where we are
                current_file = Path(__file__).resolve()
                root_path = current_file.parent.parent.parent / '.env'
                
                logger.info(f"debug: current_file={current_file}")
                logger.info(f"debug: looking for .env at {root_path}")
                
                if root_path.exists():
                    logger.info(f"debug: .env file FOUND at {root_path}")
                else:
                    logger.error(f"debug: .env file NOT FOUND at {root_path}")
                
                logger.info(f"Attempting to reload .env from {root_path}")
                load_dotenv(root_path, override=True)
                self.api_key = os.environ.get('REPHRASY_API_KEY')
            except Exception as e:
                logger.error(f"Failed to reload .env: {e}")
        
        if self.api_key:
            logger.info(f"RephrasyService initialized with API key: {self.api_key[:4]}...{self.api_key[-4:]}")
        else:
            logger.error("RephrasyService initialized WITHOUT API key")

        self.detect_url = 'https://detector.rephrasy.ai/detect_api'
        self.humanize_url = 'https://v2-humanizer.rephrasy.ai/api'
    
    def detect_ai_content(self, text: str, mode: str = "") -> Optional[Dict]:
        """
        Detect if content is AI-generated using Rephrasy API
        
        Args:
            text: The text content to analyze
            mode: Optional mode parameter for detailed results (e.g., 'depth' for sentence-level scores)
            
        Returns:
            Dict containing detection results with AI score and confidence, or None on error
        """
        if not self.api_key:
            logger.error("Cannot detect AI content: REPHRASY_API_KEY not configured")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'text': text,
                'mode': mode
            }
            
            response = requests.post(
                self.detect_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Rephrasy detection completed for {len(text)} characters")
                return result
            else:
                logger.error(f"Rephrasy Detection API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Rephrasy Detection API: {str(e)}")
            return None
    
    def humanize_content(
        self, 
        text: str, 
        model: str = "undetectable",
        language: Optional[str] = None,
        words_based_pricing: bool = True,
        return_costs: bool = True
    ) -> Optional[Dict]:
        """
        Humanize AI-generated content using Rephrasy API
        
        Args:
            text: The AI-generated text to humanize
            model: Humanization model - 'undetectable', 'SEO Model', or Writing Style ID
            language: Language name (e.g., 'English', 'German'). Auto-detected if not provided
            words_based_pricing: Enable word-based pricing (0.1 credits flat + 0.1 per 100 words)
            return_costs: Return cost information in response
            
        Returns:
            Dict containing humanized text, flesch score, and optional cost info, or None on error
        """
        if not self.api_key:
            logger.error("Cannot humanize content: REPHRASY_API_KEY not configured")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'text': text,
                'model': model,
                'words': words_based_pricing,
                'costs': return_costs
            }
            
            # Add language if specified
            if language:
                data['language'] = language
            
            response = requests.post(
                self.humanize_url,
                headers=headers,
                json=data,
                timeout=60  # Longer timeout for humanization
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Rephrasy humanization completed for {len(text)} characters")
                return result
            else:
                logger.error(f"Rephrasy Humanization API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Rephrasy Humanization API: {str(e)}")
            return None
