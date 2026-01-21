import sys
import os
import pytest
import asyncio
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.abspath('backend'))

from services.pdf_service import PDFService

@pytest.mark.asyncio
async def test_generate_pdf_async_delegation():
    """Test that generate_pdf delegates to _generate_pdf_sync via to_thread"""

    latex_content = "test latex"
    expected_bytes = b"%PDF-1.4 mock"

    # Mock the sync method
    with patch.object(PDFService, '_generate_pdf_sync', return_value=expected_bytes) as mock_sync:
        # Call the async method
        result = await PDFService.generate_pdf(latex_content, preview_mode=True)

        # Verify result
        assert result == expected_bytes

        # Verify sync method was called with correct args
        mock_sync.assert_called_once_with(latex_content, True)
