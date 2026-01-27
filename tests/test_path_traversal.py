import sys
import os
import unittest
import shutil
from unittest.mock import MagicMock, patch
from pathlib import Path
from pydantic import BaseModel

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Define Mock Models
class UserResponse(BaseModel):
    user_id: str
    email: str
    credits: int
    plan: str

# Mock dependencies BEFORE importing server
sys.modules['supabase'] = MagicMock()
sys.modules['dodopayments'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.genai'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['google.api_core'] = MagicMock()
sys.modules['google.auth'] = MagicMock()
sys.modules['bs4'] = MagicMock()
sys.modules['jwt'] = MagicMock()
sys.modules['firecrawl'] = MagicMock()
sys.modules['xhtml2pdf'] = MagicMock()
sys.modules['reportlab'] = MagicMock()
sys.modules['PyPDF2'] = MagicMock()
sys.modules['pylatex'] = MagicMock()
sys.modules['requests'] = MagicMock()

# Mock services and models
sys.modules['services.gemini_service'] = MagicMock()
sys.modules['services.pdf_service'] = MagicMock()
sys.modules['services.auth_service'] = MagicMock()
sys.modules['services.payment_service'] = MagicMock()
sys.modules['services.pexels_service'] = MagicMock()
sys.modules['services.rephrasy_service'] = MagicMock()
sys.modules['services.content_converter_service'] = MagicMock()
sys.modules['services.pdf_extractor_service'] = MagicMock()
sys.modules['services.resume_optimizer_service'] = MagicMock()
sys.modules['services.ppt_generator_service'] = MagicMock()
sys.modules['models.session'] = MagicMock()

# Mock models.user with actual Pydantic model for UserResponse
mock_user_module = MagicMock()
mock_user_module.UserResponse = UserResponse
sys.modules['models.user'] = mock_user_module

# Now import the function to test
with patch.dict(os.environ, {
    'SUPABASE_URL': 'http://mock',
    'SUPABASE_KEY': 'mock',
    'GEMINI_API_KEY': 'mock',
    'DODO_PAYMENTS_API_KEY': 'mock'
}):
    import server
    from server import serve_temp_image, ROOT_DIR
    from fastapi import HTTPException

class TestPathTraversal(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Create temp_uploads directory and a test file
        self.temp_dir = ROOT_DIR / "temp_uploads"
        self.temp_dir.mkdir(exist_ok=True)
        self.test_filename = "test_image.jpg"
        self.test_filepath = self.temp_dir / self.test_filename
        with open(self.test_filepath, "w") as f:
            f.write("fake image content")

    def tearDown(self):
        # Clean up test file
        if self.test_filepath.exists():
            self.test_filepath.unlink()

    async def test_path_traversal_blocked(self):
        """Test that accessing files outside temp_uploads is blocked"""
        # Attempt to access server.py (which exists in parent of temp_uploads)
        target_filename = "../server.py"

        # Verify the target file actually exists relative to ROOT_DIR (sanity check)
        expected_path = self.temp_dir / target_filename
        self.assertTrue(expected_path.resolve().exists(), "Target file ../server.py does not exist for test setup")

        # Expect HTTPException (404 Not Found is raised for security)
        with self.assertRaises(HTTPException) as cm:
            await serve_temp_image(target_filename)

        self.assertEqual(cm.exception.status_code, 404)
        self.assertEqual(cm.exception.detail, "Image not found")

    async def test_legitimate_access_allowed(self):
        """Test that accessing files inside temp_uploads is allowed"""
        response = await serve_temp_image(self.test_filename)

        # Verify it returns a FileResponse with correct path
        self.assertEqual(response.path.resolve(), self.test_filepath.resolve())

if __name__ == '__main__':
    unittest.main()
