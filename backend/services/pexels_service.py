import os
import logging
import requests
import asyncio
from typing import Dict, Optional
from cachetools import cached, TTLCache
from cachetools.keys import hashkey

logger = logging.getLogger(__name__)

# Global cache for Pexels searches (100 items, 1 hour TTL)
search_cache = TTLCache(maxsize=100, ttl=3600)


class PexelsService:
    """Service for interacting with Pexels API to search and fetch images"""

    def __init__(self):
        self.api_key = os.environ.get('PEXELS_API_KEY')
        self.base_url = 'https://api.pexels.com/v1'

        if not self.api_key:
            logger.warning("PEXELS_API_KEY not found in environment variables")

    @cached(search_cache, key=lambda self, *args, **kwargs: hashkey(*args, **kwargs))
    def search_images(self, query: str, per_page: int = 15, page: int = 1) -> Optional[Dict]:
        """
        Search for images on Pexels
        """
        # Fallback for missing API key or errors
        fallback_response = {
            'photos': [{
                'src': {
                    'large': f'https://dummyimage.com/1024x768/e0e0e0/000000.png&text={query.replace(" ", "+")}'
                }
            }]
        }

        if not self.api_key:
            logger.warning("PEXELS_API_KEY not found, using placeholder images")
            return fallback_response

        try:
            headers = {
                'Authorization': self.api_key
            }

            params = {
                'query': query,
                'per_page': min(per_page, 80),  # Pexels max is 80
                'page': page
            }

            response = requests.get(
                f'{self.base_url}/search',
                headers=headers,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Pexels search for '{query}' returned {len(data.get('photos', []))} results")
                if not data.get('photos'):
                    return fallback_response
                return data
            else:
                logger.error(f"Pexels API error: {response.status_code} - {response.text}")
                return fallback_response

        except Exception as e:
            logger.error(f"Error searching Pexels: {str(e)}")
            return fallback_response

    async def search_images_async(self, query: str, per_page: int = 15, page: int = 1) -> Optional[Dict]:
        """Async wrapper for search_images"""
        return await asyncio.to_thread(self.search_images, query, per_page, page)

    def get_curated_images(self, per_page: int = 15, page: int = 1) -> Optional[Dict]:
        """
        Get curated images from Pexels

        Args:
            per_page: Number of results per page (max 80)
            page: Page number

        Returns:
            Dict containing photos array and metadata, or None on error
        """
        if not self.api_key:
            logger.error("Cannot get curated images: PEXELS_API_KEY not configured")
            return None

        try:
            headers = {
                'Authorization': self.api_key
            }

            params = {
                'per_page': min(per_page, 80),
                'page': page
            }

            response = requests.get(
                f'{self.base_url}/curated',
                headers=headers,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Pexels curated returned {len(data.get('photos', []))} results")
                return data
            else:
                logger.error(f"Pexels API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting curated images: {str(e)}")
            return None
