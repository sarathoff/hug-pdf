import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Set up environment variables before importing server
os.environ["SUPABASE_URL"] = "http://mock-supabase"
os.environ["SUPABASE_KEY"] = "mock-key"
os.environ["GEMINI_API_KEY"] = "mock-key"
os.environ["DODO_PAYMENTS_API_KEY"] = "mock-key"
os.environ["JWT_SECRET"] = "mock-secret"

# Mock services
sys.modules["services.gemini_service"] = MagicMock()
sys.modules["services.pdf_service"] = MagicMock()
sys.modules["services.auth_service"] = MagicMock()
sys.modules["services.payment_service"] = MagicMock()
sys.modules["services.pexels_service"] = MagicMock()
sys.modules["dodopayments"] = MagicMock()
sys.modules["supabase"] = MagicMock()

# Mock specific classes inside modules if necessary
sys.modules["services.gemini_service"].GeminiService = MagicMock
sys.modules["services.pdf_service"].PDFService = MagicMock
sys.modules["services.auth_service"].AuthService = MagicMock
sys.modules["services.payment_service"].PaymentService = MagicMock
sys.modules["services.pexels_service"].PexelsService = MagicMock

# Adjust python path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.server import app, ROOT_DIR
from fastapi.testclient import TestClient

class TestPathTraversal(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.temp_dir = ROOT_DIR / "temp_uploads"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Create a benign file
        self.safe_file = self.temp_dir / "safe.txt"
        self.safe_file.write_text("safe content")

    def tearDown(self):
        if self.safe_file.exists():
            self.safe_file.unlink()

    def test_safe_access(self):
        response = self.client.get("/api/temp-images/safe.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"safe content")

    def test_path_traversal_server_py(self):
        # Attempt to access server.py which is one level up from temp_uploads
        # encoded as ..%2Fserver.py
        response = self.client.get("/api/temp-images/..%2Fserver.py")

        # If vulnerable, this will return 200
        if response.status_code == 200:
            print("\n[CRITICAL] Path traversal vulnerability confirmed: Accessed ../server.py")
        else:
            print(f"\n[INFO] Request to ../server.py returned {response.status_code}")

        # In a real test we assert, but here I want to see it fail first if possible,
        # or assert that it SHOULD be 404 (after fix).
        # For now, let's assert it is 404, so it fails if vulnerable.
        self.assertEqual(response.status_code, 404, "Vulnerability exists: Able to access files outside temp_uploads")

if __name__ == "__main__":
    unittest.main()
