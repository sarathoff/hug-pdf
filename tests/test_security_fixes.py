import sys
import os
import unittest
from unittest.mock import MagicMock
from pathlib import Path
import asyncio

# Setup mocks BEFORE importing backend modules
# This is necessary because backend.server imports services that require environment variables and external deps.

def setup_mocks():
    # 1. Set dummy env vars
    os.environ["GEMINI_API_KEY"] = "dummy"
    os.environ["SUPABASE_URL"] = "http://dummy.com"
    os.environ["SUPABASE_KEY"] = "dummy"
    os.environ["DODO_PAYMENTS_API_KEY"] = "dummy"
    os.environ["BACKEND_URL"] = "http://testserver"

    # 2. Mock external dependencies
    sys.modules["dodopayments"] = MagicMock()
    sys.modules["supabase"] = MagicMock()
    sys.modules["google"] = MagicMock()
    sys.modules["google.generativeai"] = MagicMock()
    sys.modules["firecrawl"] = MagicMock() # content_converter_service

    # Mock services to avoid instantiation side effects
    module_names = [
        "backend.services.payment_service",
        "backend.services.pexels_service",
        "backend.services.content_converter_service",
        "backend.services.pdf_extractor_service",
        "backend.services.resume_optimizer_service",
        "backend.services.ppt_generator_service",
        "backend.services.gemini_service",
        "backend.core.deps",
    ]
    for name in module_names:
        sys.modules[name] = MagicMock()

    # Mock routers to avoid importing them if they have dependencies
    sys.modules["backend.routers.ai"] = MagicMock()
    sys.modules["backend.routers.ai"].router = MagicMock()
    sys.modules["backend.routers.pdf"] = MagicMock()
    sys.modules["backend.routers.pdf"].router = MagicMock()

setup_mocks()

# Now we can import the target function
# Adjust sys.path to include project root
sys.path.append(os.getcwd())

from backend.server import serve_temp_image, ROOT_DIR
from fastapi import HTTPException

class TestSecurityFixes(unittest.TestCase):

    def setUp(self):
        # Create temp_uploads dir and a safe file
        self.temp_dir = ROOT_DIR / "temp_uploads"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.safe_file = self.temp_dir / "safe.txt"
        self.safe_file.write_text("safe content")

    def tearDown(self):
        # Clean up
        if self.safe_file.exists():
            self.safe_file.unlink()

    def test_serve_temp_image_path_traversal(self):
        """Test that serve_temp_image prevents path traversal."""

        # Helper to run async function
        def run_async(coro):
            return asyncio.run(coro)

        # 1. Attempt traversal to server.py (which exists in ROOT_DIR)
        # ../server.py
        with self.assertRaises(HTTPException) as cm:
            run_async(serve_temp_image("../server.py"))

        self.assertEqual(cm.exception.status_code, 404)

        # 2. Attempt traversal with encoded characters?
        # The function receives decoded string from FastAPI, but we test logic here.
        # If we pass "..", checks should fail.

        # 3. Test valid access
        response = run_async(serve_temp_image("safe.txt"))
        self.assertTrue(response.path.name == "safe.txt")

    def test_serve_temp_image_absolute_path(self):
        """Test that absolute paths are also rejected if outside temp_uploads."""
        def run_async(coro):
            return asyncio.run(coro)

        # Try to pass full path to server.py
        server_py = ROOT_DIR / "server.py"
        with self.assertRaises(HTTPException) as cm:
            run_async(serve_temp_image(str(server_py)))

        self.assertEqual(cm.exception.status_code, 404)

if __name__ == '__main__':
    unittest.main()
