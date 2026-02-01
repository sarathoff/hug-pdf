import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.pexels_service import PexelsService, search_cache  # noqa: E402


class TestPexelsService:

    def setup_method(self):
        # Clear cache before each test
        search_cache.clear()

    @patch('requests.get')
    def test_search_images_sync_cached(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'photos': [{'src': {'large': 'url'}}]
        }
        mock_get.return_value = mock_response

        service = PexelsService()
        service.api_key = "test_key"

        # First call
        result1 = service.search_images("cat")
        assert result1['photos'][0]['src']['large'] == 'url'

        # Second call (should be cached)
        result2 = service.search_images("cat")
        assert result2 == result1

        # Verify requests.get was called ONLY ONCE
        mock_get.assert_called_once()

    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_search_images_async(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'photos': [{'src': {'large': 'async_url'}}]
        }
        mock_get.return_value = mock_response

        service = PexelsService()
        service.api_key = "test_key"

        result = await service.search_images_async("dog")
        assert result['photos'][0]['src']['large'] == 'async_url'
