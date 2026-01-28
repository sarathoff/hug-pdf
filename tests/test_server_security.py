import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to sys.path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

# Mock environment variables to avoid validation errors
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy-key"
os.environ["DODO_PAYMENTS_API_KEY"] = "dummy-key"
os.environ["GEMINI_API_KEY"] = "dummy-key"

# Mock dependencies before importing server
sys.modules["supabase"] = MagicMock()
sys.modules["dodopayments"] = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["google.api_core"] = MagicMock()
sys.modules["google.auth"] = MagicMock()
sys.modules["bs4"] = MagicMock()
sys.modules["jwt"] = MagicMock()
sys.modules["firecrawl"] = MagicMock()
sys.modules["xhtml2pdf"] = MagicMock()
sys.modules["reportlab"] = MagicMock()
sys.modules["PyPDF2"] = MagicMock()
sys.modules["email_validator"] = MagicMock()
sys.modules["bcrypt"] = MagicMock()
sys.modules["passlib"] = MagicMock()
sys.modules["passlib.context"] = MagicMock()
sys.modules["requests"] = MagicMock()

# Now import app
from server import app, ROOT_DIR

# We need to override the ROOT_DIR in the server module because it's hardcoded to __file__.parent
# But since we imported it, we can patch it?
# server.ROOT_DIR is a Path object.
# The server logic uses ROOT_DIR from the module scope.
# We can try to patch it, but it might be used at module level?
# No, it's used inside the function `serve_temp_image` as `ROOT_DIR`.
# So patching `server.ROOT_DIR` should work.

import server
server.ROOT_DIR = backend_path # Ensure it points to actual backend dir so temp_uploads path logic works
# But wait, our test wants to create temp_uploads in a controllable place?
# We can point ROOT_DIR to a temporary directory for the test.

client = TestClient(app)

@pytest.fixture
def mock_root_dir(tmp_path):
    # Patch ROOT_DIR in server module to point to tmp_path
    original_root = server.ROOT_DIR
    server.ROOT_DIR = tmp_path

    # Create temp_uploads
    (tmp_path / "temp_uploads").mkdir()

    yield tmp_path

    server.ROOT_DIR = original_root

def test_serve_temp_image_path_traversal(mock_root_dir):
    """Test that path traversal is blocked in /temp-images/ endpoint"""
    # Create a dummy file inside temp_uploads
    (mock_root_dir / "temp_uploads" / "safe.jpg").write_text("safe content")

    # Create a secret file outside
    (mock_root_dir / "secret.txt").write_text("THIS IS SECRET")

    # Test valid access
    response = client.get("/api/temp-images/safe.jpg")
    assert response.status_code == 200
    assert response.content == b"safe content"

    # Test path traversal
    response = client.get("/api/temp-images/../secret.txt")
    assert response.status_code == 404

    # Verify no content leaked
    assert b"THIS IS SECRET" not in response.content

def test_serve_temp_image_deep_traversal(mock_root_dir):
    """Test deep traversal"""
    response = client.get("/api/temp-images/../../../etc/passwd")
    assert response.status_code == 404
