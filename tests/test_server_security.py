
import sys
import os
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# --- MOCKING DEPENDENCIES ---
mock_modules = [
    "supabase",
    "dodopayments",
    "google",
    "google.genai",
    "google.generativeai",
    "google.api_core",
    "google.auth",
    "bs4",
    "jwt",
    "firecrawl",
    "xhtml2pdf",
    "reportlab",
    "PyPDF2",
    "requests", # Added requests
    "boto3",    # Added potentially needed
    "botocore",
]

for mod in mock_modules:
    sys.modules[mod] = MagicMock()

# Mock internal services as TOP LEVEL modules because of sys.path hack in server.py
sys.modules["services"] = MagicMock()
sys.modules["services.payment_service"] = MagicMock()
sys.modules["services.pexels_service"] = MagicMock()
sys.modules["services.content_converter_service"] = MagicMock()
sys.modules["services.pdf_extractor_service"] = MagicMock()
sys.modules["services.resume_optimizer_service"] = MagicMock()
sys.modules["services.ppt_generator_service"] = MagicMock()
sys.modules["services.gemini_service"] = MagicMock()

# Also mock backend-namespaced services just in case
sys.modules["backend.services"] = MagicMock()
sys.modules["backend.services.payment_service"] = MagicMock()
sys.modules["backend.services.pexels_service"] = MagicMock()
sys.modules["backend.services.content_converter_service"] = MagicMock()
sys.modules["backend.services.pdf_extractor_service"] = MagicMock()
sys.modules["backend.services.resume_optimizer_service"] = MagicMock()
sys.modules["backend.services.ppt_generator_service"] = MagicMock()
sys.modules["backend.services.gemini_service"] = MagicMock()

# Mock deps
sys.modules["backend.core.deps"] = MagicMock()
sys.modules["backend.routers.ai"] = MagicMock()
sys.modules["backend.routers.pdf"] = MagicMock()

# Setup mocks for class imports
from services.payment_service import PaymentService
from services.pexels_service import PexelsService
from services.content_converter_service import ContentConverterService
from services.pdf_extractor_service import PDFExtractorService
from services.resume_optimizer_service import ResumeOptimizerService
from services.ppt_generator_service import PPTGeneratorService
from services.gemini_service import GeminiService

# Import App
try:
    from backend.server import app, ROOT_DIR
except ImportError as e:
    print(f"Import failed: {e}")
    raise

client = TestClient(app)

# --- TESTS ---

def test_serve_temp_image_traversal():
    """
    Verify that path traversal attempts are blocked.
    """
    # Create a dummy secret file outside temp_uploads
    secret_file = ROOT_DIR / "secret_test.txt"
    with open(secret_file, "w") as f:
        f.write("CONFIDENTIAL")

    try:
        # payload = "../secret_test.txt"
        response = client.get("/api/temp-images/..%2Fsecret_test.txt")

        print(f"Traversal Status: {response.status_code}")
        if response.status_code == 200 and "CONFIDENTIAL" in response.text:
             pytest.fail("Vulnerability Reproduced: Accessed secret file via traversal")

        assert response.status_code in [403, 404], "Should return 403 (Forbidden) or 404 (Not Found)"

    finally:
        if secret_file.exists():
            os.remove(secret_file)

def test_upload_image_extension_whitelist():
    """
    Verify that only whitelisted extensions are allowed.
    """
    from backend.server import get_current_user
    app.dependency_overrides[get_current_user] = lambda: {"user_id": "test_user", "email": "test@example.com"}

    # 1. Valid upload
    files = {'file': ('test.jpg', b'fake content', 'image/jpeg')}
    response = client.post("/api/upload-image", files=files)
    assert response.status_code == 200

    # 2. Invalid extension (PHP)
    files_evil = {'file': ('evil.php', b'<?php echo "hacked"; ?>', 'application/x-php')}
    response_evil = client.post("/api/upload-image", files=files_evil)

    assert response_evil.status_code == 400, "Should block .php extension"
    assert "Invalid file type" in response_evil.text

    # 3. Double extension
    files_double = {'file': ('evil.jpg.php', b'bad', 'application/x-php')}
    response_double = client.post("/api/upload-image", files=files_double)
    if response_double.status_code != 200:
         assert response_double.status_code == 400

    app.dependency_overrides = {}
