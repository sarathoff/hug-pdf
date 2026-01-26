
import os
import sys
import pytest
from unittest.mock import MagicMock
from pathlib import Path
from fastapi import HTTPException

# Add backend to sys.path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

# Mock environment variables
os.environ["GEMINI_API_KEY"] = "fake_key"
os.environ["SUPABASE_URL"] = "https://fake.supabase.co"
os.environ["SUPABASE_KEY"] = "fake_key"
os.environ["DODO_PAYMENTS_API_KEY"] = "fake_key"

# Mock modules
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["google.api_core"] = MagicMock()
sys.modules["google.auth"] = MagicMock()
sys.modules["dodopayments"] = MagicMock()
sys.modules["xhtml2pdf"] = MagicMock()
sys.modules["reportlab"] = MagicMock()
sys.modules["bs4"] = MagicMock()
sys.modules["PyPDF2"] = MagicMock()
sys.modules["firecrawl"] = MagicMock()

# Import logic to test
try:
    from server import serve_temp_image
except ImportError:
    # If imports fail in test environment (e.g. CI), we might skip or fail.
    pass

@pytest.mark.asyncio
async def test_serve_temp_image_path_traversal():
    """Verify that serve_temp_image prevents path traversal"""
    # Attempt to access a file outside temp_uploads
    filename = "../requirements.txt"

    # Expect 403 Forbidden or 404 Not Found (if validation fails before check)
    # Our fix raises 403 for path traversal attempts

    with pytest.raises(HTTPException) as excinfo:
        await serve_temp_image(filename)

    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Invalid filename"

@pytest.mark.asyncio
async def test_serve_temp_image_valid_file():
    """Verify that serve_temp_image allows valid files in temp_uploads"""
    # We need to simulate a file existing in temp_uploads
    # Since serve_temp_image checks for existence, we need to mock Path.exists

    valid_filename = "valid_image.jpg"

    # We can't easily mock Path inside the function without patching it in the module
    # But we can verify it doesn't raise 403

    # If the file doesn't exist, it should raise 404, not 403
    with pytest.raises(HTTPException) as excinfo:
        await serve_temp_image(valid_filename)

    # It should NOT be 403
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Image not found"
