import pytest
import asyncio
import time
from unittest.mock import MagicMock, patch
import os
import sys
from pathlib import Path

# Add backend to sys.path to ensure imports work if run from root
sys.path.append(str(Path(__file__).parent.parent))

from services.pexels_service import PexelsService

# Mock env vars
os.environ["PEXELS_API_KEY"] = "test-key"

@pytest.mark.asyncio
async def test_search_images_async_non_blocking():
    """
    Verify that search_images is async and does NOT block the event loop.
    """
    # Mock requests.get to simulate latency (BLOCKING)
    def mocked_requests_get(*args, **kwargs):
        time.sleep(0.5) # Block for 0.5s
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"photos": []}
        return mock_response

    with patch('requests.get', side_effect=mocked_requests_get):
        service = PexelsService()

        # Background heartbeat to check for blocking
        async def heartbeat():
            ticks = 0
            start_time = time.time()
            # Run for slightly longer than the simulated block to capture ticks
            while time.time() - start_time < 0.7:
                ticks += 1
                await asyncio.sleep(0.1)
            return ticks

        # Start heartbeat
        heartbeat_task = asyncio.create_task(heartbeat())

        # Allow heartbeat to start
        await asyncio.sleep(0.05)

        # Call the service method (should be non-blocking now)
        start_time = time.time()
        # This await should yield control, allowing heartbeat to run while to_thread runs in background
        await service.search_images("test")
        end_time = time.time()

        ticks = await heartbeat_task

        duration = end_time - start_time
        print(f"Call duration: {duration:.2f}s, Heartbeat ticks: {ticks}")

        # If it was blocking, ticks would be minimal (maybe 1 just before block).
        # With 0.5s block and 0.1s sleep, we expect ~5 ticks.
        # We assert > 2 to be safe.
        assert ticks > 2, f"Event loop was blocked! Heartbeat only ran {ticks} times during {duration:.2f}s call."

@pytest.mark.asyncio
async def test_search_images_sync_method_exists():
    """Verify sync method still exists and works (mocked)"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"photos": [{"id": 123}]}

        service = PexelsService()
        # Calling the _sync method directly
        result = service.search_images_sync("test")
        assert result == {"photos": [{"id": 123}]}
        mock_get.assert_called_once()
