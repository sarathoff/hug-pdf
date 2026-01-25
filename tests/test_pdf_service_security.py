import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import shutil

# Set up paths
BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.append(str(BACKEND_DIR))

# Mock environment variables
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "mock-key"

# Import PDFService
try:
    from services.pdf_service import PDFService
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_download_image_path_traversal():
    print("Testing PDFService Path Traversal Vulnerability...")

    # Mock temp_dir
    temp_dir = Path("/tmp/mock_temp_dir")

    # 1. Test Path Traversal via filename in URL
    # Malicious URL: http://localhost/temp-images/../server.py
    # If vulnerable, it would try to copy ../server.py (which resolves to server.py)

    # We need to verify that it returns None and logs a warning

    # Since _download_image checks if source_path exists, we need to ensure it 'exists' for the test
    # BUT if our security check works, it should fail BEFORE checking existence

    url = "http://localhost/temp-images/../server.py"

    with patch("services.pdf_service.shutil.copy") as mock_copy:
        result = PDFService._download_image(url, temp_dir)

        if result is None:
            print("✅ Vulnerability blocked (Result is None)")
        else:
            print(f"❌ Vulnerability NOT blocked (Result: {result})")

        mock_copy.assert_not_called()

    # 2. Test valid path
    # We need to create a dummy file in temp_uploads to test success
    # But since we are mocking, we can just check if it passes security check

    valid_url = "http://localhost/temp-images/safe.jpg"

    # We need to mock .exists() to return True for safe.jpg
    # and False for others, or just verify logic flow.
    # Actually, we can use a real file.

    temp_uploads = BACKEND_DIR / "temp_uploads"
    temp_uploads.mkdir(exist_ok=True)
    (temp_uploads / "safe.jpg").touch()

    with patch("services.pdf_service.shutil.copy") as mock_copy:
        result = PDFService._download_image(valid_url, temp_dir)

        # It should return a path
        if result:
            print(f"✅ Normal access works (Result: {result})")
            mock_copy.assert_called()
        else:
            print("❌ Normal access failed")

if __name__ == "__main__":
    test_download_image_path_traversal()
