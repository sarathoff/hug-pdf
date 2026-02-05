import sys
import os
import unittest
from unittest.mock import MagicMock

# --- MOCKING SETUP BEFORE IMPORT ---
# We must mock dependencies that require external services or env vars
sys.modules["supabase"] = MagicMock()
sys.modules["dodopayments"] = MagicMock()
sys.modules["google"] = MagicMock()
# Mock google.genai and others as objects inside google mock if needed, but separate entries are safer
sys.modules["google.genai"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["firecrawl"] = MagicMock()
sys.modules["xhtml2pdf"] = MagicMock()
sys.modules["reportlab"] = MagicMock()
sys.modules["PyPDF2"] = MagicMock()
sys.modules["pylatex"] = MagicMock()
sys.modules["boto3"] = MagicMock()
sys.modules["botocore"] = MagicMock()
sys.modules["dotenv"] = MagicMock()
sys.modules["bcrypt"] = MagicMock()
sys.modules["passlib"] = MagicMock()
sys.modules["email_validator"] = MagicMock()

# Mock backend services to avoid initialization logic
# We mock the modules themselves so imports return mocks
mock_services = MagicMock()
sys.modules["backend.services.payment_service"] = MagicMock()
sys.modules["backend.services.pexels_service"] = MagicMock()
sys.modules["backend.services.content_converter_service"] = MagicMock()
sys.modules["backend.services.pdf_extractor_service"] = MagicMock()
sys.modules["backend.services.resume_optimizer_service"] = MagicMock()
sys.modules["backend.services.ppt_generator_service"] = MagicMock()
sys.modules["backend.services.gemini_service"] = MagicMock()

# Mock the 'services' alias versions as well
sys.modules["services.payment_service"] = MagicMock()
sys.modules["services.pexels_service"] = MagicMock()
sys.modules["services.content_converter_service"] = MagicMock()
sys.modules["services.pdf_extractor_service"] = MagicMock()
sys.modules["services.resume_optimizer_service"] = MagicMock()
sys.modules["services.ppt_generator_service"] = MagicMock()
sys.modules["services.gemini_service"] = MagicMock()
sys.modules["services.web_scraper_service"] = MagicMock()
sys.modules["services.auth_service"] = MagicMock()
sys.modules["services.credit_service"] = MagicMock()
sys.modules["services.perplexity_service"] = MagicMock()
sys.modules["services.cache_service"] = MagicMock()

# Also mock backend.routers.ai and pdf just in case they have deep dependencies
# backend.server imports them. We want backend.server to run, so we can let them import
# but ensure their dependencies are mocked (which they are, via sys.modules above).

# Env vars
os.environ["GEMINI_API_KEY"] = "fake"
os.environ["SUPABASE_URL"] = "https://fake.supabase.co"
os.environ["SUPABASE_KEY"] = "fake"
os.environ["DODO_PAYMENTS_API_KEY"] = "fake"
os.environ["DODO_PAYMENTS_WEBHOOK_KEY"] = "fake"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "fake"
os.environ["BACKEND_URL"] = "http://testserver"

# Now import the app
try:
    from backend.server import app, ROOT_DIR
    from fastapi.testclient import TestClient
    from backend.core.deps import get_current_user
except ImportError as e:
    import traceback
    traceback.print_exc()
    print(f"FAILED TO IMPORT APP: {e}")
    sys.exit(1)

class TestSecurityFixes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        # Override get_current_user to bypass auth for upload endpoint
        # The upload_image endpoint requires get_current_user
        app.dependency_overrides[get_current_user] = lambda: {"user_id": "test", "email": "test@example.com"}

    def test_path_traversal(self):
        # Create a dummy file in root to try to access
        # ROOT_DIR is where server.py is.
        # temp_uploads is ROOT_DIR/temp_uploads

        # We try to access ../server.py relative to temp_uploads
        # We don't need to actually create server.py, it exists.

        # Ensure temp_uploads exists
        (ROOT_DIR / "temp_uploads").mkdir(exist_ok=True)

        # Attempt to access the server source code
        # Note: HTTP clients normalize paths, so we must be careful.
        # However, malicious actors send raw bytes.
        # We can try URL encoding the dots: %2e%2e%2fserver.py
        # FastAPI/Starlette will decode this to ../server.py and pass it to filename param.

        response = self.client.get("/api/temp-images/%2e%2e%2fserver.py")

        # VULNERABLE behavior: 200 OK (file served)
        # SECURE behavior: 404 Not Found (or 403)

        # We assert what we expect NOW (Vulnerable)
        # If it's already fixed, this test will fail, which is good info.
        if response.status_code == 200:
             print("\n[VULNERABILITY CONFIRMED] Path traversal successful (accessed ../server.py)")
        else:
             print(f"\n[SECURE?] Path traversal blocked (Status: {response.status_code})")

        # Assertion
        self.assertNotEqual(response.status_code, 200, "Path traversal should not succeed")
        self.assertTrue(response.status_code in [400, 403, 404], f"Unexpected status code: {response.status_code}")

    def test_arbitrary_file_upload(self):
        # Malicious file (HTML with XSS potential)
        files = {
            "file": ("exploit.html", "<html><script>alert(1)</script></html>", "text/html")
        }

        response = self.client.post("/api/upload-image", files=files)

        # VULNERABLE behavior: 200 OK
        if response.status_code == 200:
            print("\n[VULNERABILITY CONFIRMED] Arbitrary file upload successful")
            data = response.json()
            print(f"Uploaded to: {data.get('url')}")
        else:
            print(f"\n[SECURE?] Upload blocked (Status: {response.status_code})")

        # Assertion for verification phase
        self.assertEqual(response.status_code, 400, "Should be blocked with 400 Bad Request")
        self.assertIn("Invalid file type", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
