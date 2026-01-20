import sys
import os
from pathlib import Path
from unittest.mock import MagicMock
import types
import asyncio
from fastapi import HTTPException

# Create mock for google package
google = types.ModuleType("google")
sys.modules["google"] = google

# Create mock for google.genai
genai = MagicMock()
sys.modules["google.genai"] = genai
google.genai = genai # Allow "from google import genai"

# Mock types in google.genai
genai.types = MagicMock()

# Mock google.api_core
sys.modules["google.api_core"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()

# Mock dodopayments
sys.modules['dodopayments'] = MagicMock()

# Mock bs4
sys.modules['bs4'] = MagicMock()

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

# Mock env vars to avoid startup errors
os.environ['SUPABASE_URL'] = 'https://example.supabase.co'
os.environ['SUPABASE_KEY'] = 'fake-key'
os.environ['GEMINI_API_KEY'] = 'fake-key'
os.environ['DODO_PAYMENTS_API_KEY'] = 'fake-key'

# Import TestClient after mocking
from fastapi.testclient import TestClient

try:
    from server import app, ROOT_DIR, serve_temp_image
except ImportError as e:
    print(f"ImportError during setup: {e}")
    sys.exit(1)

client = TestClient(app)

def test_path_traversal_server_direct():
    # Direct function call to avoid client URL normalization issues
    # We want to ensure serve_temp_image raises 403 for traversal

    filename = "../../.env"

    try:
        asyncio.run(serve_temp_image(filename))
        print("FAIL: serve_temp_image did not raise HTTPException")
    except HTTPException as e:
        if e.status_code == 403:
            print("PASS: serve_temp_image raised 403 Forbidden")
        else:
            print(f"FAIL: serve_temp_image raised {e.status_code} (expected 403)")
            raise e
    except Exception as e:
        print(f"FAIL: serve_temp_image raised unexpected exception: {e}")
        raise e

def test_valid_image_access():
    # Setup a dummy file in temp_uploads
    temp_dir = ROOT_DIR / "temp_uploads"
    temp_dir.mkdir(exist_ok=True)

    test_file = temp_dir / "test_safe.txt"
    test_file.write_text("safe content")

    try:
        response = client.get("/api/temp-images/test_safe.txt")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Detail: {response.text}"
        assert response.content == b"safe content"
    finally:
        if test_file.exists():
            test_file.unlink()

def test_pdf_service_path_traversal():
    from services.pdf_service import PDFService

    temp_dir = Path("temp_test_dir")
    temp_dir.mkdir(exist_ok=True)

    try:
        # malicious url
        url = "http://localhost/temp-images/../../.env"

        result = PDFService._download_image(url, temp_dir)

        # Should return None because of security check
        assert result is None, "Expected None (blocked), got a path"

    finally:
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    try:
        print("Running test_path_traversal_server_direct...")
        test_path_traversal_server_direct()
        print("PASS")

        print("Running test_valid_image_access...")
        test_valid_image_access()
        print("PASS")

        print("Running test_pdf_service_path_traversal...")
        test_pdf_service_path_traversal()
        print("PASS")

    except Exception as e:
        print(f"FAIL: {e}")
        # import traceback
        # traceback.print_exc()
        sys.exit(1)
