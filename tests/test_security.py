import sys
import os
import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock
from fastapi import HTTPException

# Add backend to sys.path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

# Mock modules BEFORE importing server
sys.modules["supabase"] = MagicMock()
sys.modules["dodopayments"] = MagicMock()

# Mock services
mock_services = [
    "services.gemini_service",
    "services.pdf_service",
    "services.auth_service",
    "services.payment_service",
    "services.pexels_service",
    "services.rephrasy_service",
    "services.web_scraper_service",
]

for service in mock_services:
    m = MagicMock()
    sys.modules[service] = m
    class_name = service.split('.')[-1].replace('_', ' ').title().replace(' ', '')
    setattr(m, class_name, MagicMock())

# Mock os.environ before import
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "fake-key"
os.environ["GEMINI_API_KEY"] = "fake-key"
os.environ["DODO_PAYMENTS_API_KEY"] = "fake-key"
os.environ["BACKEND_URL"] = "http://localhost:8000"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "fake-role-key"

# Import app
try:
    from server import serve_temp_image
except ImportError:
    from backend.server import serve_temp_image

@pytest.mark.asyncio
async def test_path_traversal_prevention():
    """Test that path traversal attempts are blocked"""
    malicious_filename = "../requirements.txt"

    with pytest.raises(HTTPException) as excinfo:
        await serve_temp_image(malicious_filename)

    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Invalid file path"

@pytest.mark.asyncio
async def test_valid_file_access():
    """Test that valid files can be accessed"""
    # Create a dummy file in temp_uploads for testing
    temp_dir = backend_path / "temp_uploads"
    temp_dir.mkdir(exist_ok=True)
    test_file = temp_dir / "test_safe.txt"
    test_file.write_text("safe content")

    try:
        response = await serve_temp_image("test_safe.txt")
        assert response.path == test_file
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
