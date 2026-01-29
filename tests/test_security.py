import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Set up mocks BEFORE importing app
mock_modules = [
    "supabase", "dodopayments", "google", "google.genai",
    "google.generativeai", "google.api_core", "google.auth",
    "bs4", "jwt", "firecrawl", "xhtml2pdf", "reportlab", "PyPDF2"
]

for mod in mock_modules:
    sys.modules[mod] = MagicMock()

# Mock environment variables
os.environ["SUPABASE_URL"] = "http://mock-supabase"
os.environ["SUPABASE_KEY"] = "mock-key"
os.environ["DODO_PAYMENTS_API_KEY"] = "mock-dodo"
os.environ["BACKEND_URL"] = "http://localhost:8000"
os.environ["GEMINI_API_KEY"] = "mock-gemini-key"

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
sys.path.append(backend_path)

# Now import app
try:
    from server import app
    from services.pdf_service import PDFService
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

from fastapi.testclient import TestClient

client = TestClient(app)

class TestSecurity(unittest.TestCase):
    def test_upload_malicious_file_extension(self):
        """Test that uploading a file with a non-image extension is rejected."""
        files = {'file': ('evil.html', '<html>alert(1)</html>', 'text/html')}
        response = client.post("/api/upload-image", files=files)
        # Expect 400 Bad Request (Security Fix)
        # Currently it might be 200, so we assert 400 to verify the fix works when applied.
        self.assertEqual(response.status_code, 400, "Should reject .html files")

    def test_upload_malicious_content_type(self):
        """Test that uploading a file with a non-image content type is rejected."""
        files = {'file': ('test.jpg', '<html>alert(1)</html>', 'text/html')}
        response = client.post("/api/upload-image", files=files)
        self.assertEqual(response.status_code, 400, "Should reject text/html content type")

    def test_pdf_service_lfi_prevention(self):
        """Test that PDFService prevents LFI."""
        from pathlib import Path
        import shutil

        # Setup temp environment
        temp_uploads = Path(backend_path) / "temp_uploads"
        temp_uploads.mkdir(exist_ok=True)

        # Create a secret file outside temp_uploads
        secret_file = Path(backend_path) / "secret.txt"
        with open(secret_file, "w") as f:
            f.write("SECRET")

        try:
            # Construct a URL that points to the secret file via traversal
            # logic in PDFService:
            # filename = url.split('/temp-images/')[-1].split('?')[0]
            # path = ... / "temp_uploads" / filename

            url = "http://localhost:8000/api/temp-images/../secret.txt"

            # Create a mock temp dir for download
            with unittest.mock.patch('shutil.copy') as mock_copy:
                dest_dir = Path("/tmp/mock_pdf_gen")

                # Call the method directly
                result = PDFService._download_image(url, dest_dir)

                # Should return None because of security check
                self.assertIsNone(result, "Should return None for traversal attempt")

                # Ensure copy was NOT called
                mock_copy.assert_not_called()

        finally:
            if secret_file.exists():
                secret_file.unlink()

if __name__ == '__main__':
    unittest.main()
