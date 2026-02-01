
import sys
import os
import shutil
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path
from fastapi.testclient import TestClient
from fastapi import UploadFile, HTTPException

# --- Mocking Dependencies BEFORE importing server.py ---
# This ensures that we don't need the actual environment or external services.

sys.modules["dodopayments"] = MagicMock()
sys.modules["backend.services.payment_service"] = MagicMock()
sys.modules["backend.services.pexels_service"] = MagicMock()
sys.modules["backend.services.content_converter_service"] = MagicMock()
sys.modules["backend.services.pdf_extractor_service"] = MagicMock()
sys.modules["backend.services.resume_optimizer_service"] = MagicMock()
sys.modules["backend.services.ppt_generator_service"] = MagicMock()
sys.modules["backend.services.gemini_service"] = MagicMock()
sys.modules["backend.routers.ai"] = MagicMock()
sys.modules["backend.routers.pdf"] = MagicMock()
sys.modules["backend.core.deps"] = MagicMock()

# Mock settings
mock_config = MagicMock()
mock_config.settings.DODO_PAYMENTS_API_KEY = "mock_key"
sys.modules["backend.core.config"] = mock_config

# Import the app
from backend.server import app, ROOT_DIR, serve_temp_image

class TestSecurityFixes(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.temp_uploads_dir = ROOT_DIR / "temp_uploads"
        # Ensure temp dir exists for tests
        self.temp_uploads_dir.mkdir(exist_ok=True)

        # Create a dummy file in temp_uploads
        self.test_filename = "safe_image.jpg"
        self.test_filepath = self.temp_uploads_dir / self.test_filename
        with open(self.test_filepath, "wb") as f:
            f.write(b"fake image content")

        # Create a secret file in root to try to read
        self.secret_filename = "secret_file.txt"
        self.secret_filepath = ROOT_DIR / self.secret_filename
        with open(self.secret_filepath, "w") as f:
            f.write("SECRET_CONTENT")

    def tearDown(self):
        # Clean up
        if self.test_filepath.exists():
            self.test_filepath.unlink()
        if self.secret_filepath.exists():
            self.secret_filepath.unlink()
        # Clean up any other files created in temp_uploads
        for item in self.temp_uploads_dir.iterdir():
            if item.name.startswith("test_") or item.name == self.test_filename:
                try:
                    item.unlink()
                except:
                    pass

    async def test_path_traversal_vulnerability(self):
        """
        Verify that we can (currently) or cannot (after fix) access files outside temp_uploads.
        """
        # Call the function directly to avoid client path normalization
        filename = f"../{self.secret_filename}"

        try:
            response = await serve_temp_image(filename)
            # Check if the response path points to the secret file
            if response.path == self.secret_filepath:
                print("VULNERABILITY CONFIRMED: Path Traversal logic allows access.")
            else:
                # Should not happen if vulnerable
                print(f"Served path: {response.path}")

        except HTTPException as e:
            if e.status_code == 404:
                 # In vulnerable code, if it doesn't find file, it raises 404.
                 # But our secret file exists at the traversed path.
                 print("HTTPException 404: File not found (or traversal blocked?)")
            elif e.status_code == 400:
                print("VULNERABILITY FIXED: Path Traversal blocked (400).")
            else:
                 print(f"HTTPException {e.status_code}")

    def test_file_upload_extension_vulnerability(self):
        """
        Verify that we can (currently) or cannot (after fix) upload dangerous files.
        """
        # Mock user authentication
        app.dependency_overrides[sys.modules["backend.core.deps"].get_current_user] = lambda: {"user_id": "123"}

        # Try to upload a python script
        files = {"file": ("malicious.py", b"print('hacked')", "text/x-python")}
        response = self.client.post("/api/upload-image", files=files)

        if response.status_code == 200:
            print("VULNERABILITY CONFIRMED: Dangerous file upload allowed.")
            # Check if file was created
            uploaded_filename = response.json()["url"].split("/")[-1]
            uploaded_filepath = self.temp_uploads_dir / uploaded_filename
            self.assertTrue(uploaded_filepath.exists())
            # Cleanup
            uploaded_filepath.unlink()
        else:
             print("VULNERABILITY FIXED: Dangerous file upload blocked.")
             self.assertNotEqual(response.status_code, 200)

        # Try to upload a valid image
        files_valid = {"file": ("valid.jpg", b"image content", "image/jpeg")}
        response_valid = self.client.post("/api/upload-image", files=files_valid)
        self.assertEqual(response_valid.status_code, 200, "Valid image upload should succeed")

        # Cleanup valid upload
        if response_valid.status_code == 200:
             uploaded_filename = response_valid.json()["url"].split("/")[-1]
             uploaded_filepath = self.temp_uploads_dir / uploaded_filename
             if uploaded_filepath.exists():
                 uploaded_filepath.unlink()

        app.dependency_overrides = {}

if __name__ == "__main__":
    unittest.main()
