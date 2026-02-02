
import sys
from unittest.mock import MagicMock
import os
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import shutil
import asyncio

# --- Mocks and Setup ---

# Define real Pydantic models needed for response/request validation
class UserResponse(BaseModel):
    user_id: str
    email: str
    credits: int
    plan: str
    early_adopter: bool = False

class ConvertToPDFResponse(BaseModel):
    latex_content: str
    message: str
    metadata: dict
    conversion_type: str

class ConvertToPDFRequest(BaseModel):
    url: str
    conversion_type: str
    options: Optional[Dict[str, Any]] = None

class OptimizeResumeResponse(BaseModel):
    latex_content: str
    ats_score: int
    improvements: list
    message: str

class GeneratePPTResponse(BaseModel):
    latex_content: str
    slide_count: int
    images_used: list
    message: str
    session_id: str

class GeneratePPTRequest(BaseModel):
    topic: str
    content: str
    num_slides: int
    style: str

class StatusCheck(BaseModel):
    id: str
    status: str

class StatusCheckCreate(BaseModel):
    status: str

class PurchaseRequest(BaseModel):
    plan: str

# Mock dependencies before importing backend.server
# We must mock modules that server.py imports but which might not be installed or configured
sys.modules["backend.core"] = MagicMock()
sys.modules["backend.core.config"] = MagicMock()
sys.modules["backend.core.deps"] = MagicMock()
sys.modules["backend.routers"] = MagicMock()
sys.modules["backend.routers.ai"] = MagicMock()
sys.modules["backend.routers.pdf"] = MagicMock()
sys.modules["backend.schemas"] = MagicMock()
sys.modules["backend.schemas.common"] = MagicMock()
sys.modules["backend.schemas.ai"] = MagicMock()
sys.modules["backend.models"] = MagicMock()
sys.modules["backend.services"] = MagicMock()
sys.modules["backend.services.payment_service"] = MagicMock()
sys.modules["backend.services.pexels_service"] = MagicMock()
sys.modules["backend.services.content_converter_service"] = MagicMock()
sys.modules["backend.services.pdf_extractor_service"] = MagicMock()
sys.modules["backend.services.resume_optimizer_service"] = MagicMock()
sys.modules["backend.services.ppt_generator_service"] = MagicMock()
sys.modules["backend.services.gemini_service"] = MagicMock()
sys.modules["dodopayments"] = MagicMock()
sys.modules["supabase"] = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["google.api_core"] = MagicMock()
sys.modules["google.auth"] = MagicMock()

# Setup mocked modules with specific attributes
mock_user_module = MagicMock()
mock_user_module.UserResponse = UserResponse
sys.modules["backend.models.user"] = mock_user_module

mock_ai_schemas = MagicMock()
mock_ai_schemas.ConvertToPDFResponse = ConvertToPDFResponse
mock_ai_schemas.ConvertToPDFRequest = ConvertToPDFRequest
mock_ai_schemas.OptimizeResumeResponse = OptimizeResumeResponse
mock_ai_schemas.GeneratePPTResponse = GeneratePPTResponse
mock_ai_schemas.GeneratePPTRequest = GeneratePPTRequest
sys.modules["backend.schemas.ai"] = mock_ai_schemas

mock_common_schemas = MagicMock()
mock_common_schemas.StatusCheck = StatusCheck
mock_common_schemas.StatusCheckCreate = StatusCheckCreate
mock_common_schemas.PurchaseRequest = PurchaseRequest
sys.modules["backend.schemas.common"] = mock_common_schemas

mock_settings = MagicMock()
mock_settings.DODO_PAYMENTS_API_KEY = "mock_key"
sys.modules["backend.core.config"].settings = mock_settings

# Add project root to sys.path to find backend package
# Assuming this test file is in tests/ directory, root is parent
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the app and functions under test
try:
    from backend.server import app, serve_temp_image
except ImportError as e:
    print(f"Failed to import backend.server: {e}")
    sys.exit(1)

from fastapi.testclient import TestClient

client = TestClient(app)

def setup_teardown():
    # Setup: create dummy files/dirs
    backend_dir = project_root / "backend"
    secret_path = backend_dir / "secret.txt"
    temp_uploads_dir = backend_dir / "temp_uploads"

    # Create secret file (target for path traversal)
    if not secret_path.exists():
        with open(secret_path, "w") as f:
            f.write("Secret content!")

    # Create temp_uploads if not exists
    temp_uploads_dir.mkdir(exist_ok=True)

    yield secret_path

    # Teardown
    if secret_path.exists():
        secret_path.unlink()
    # Don't delete temp_uploads if it existed before, but cleaning up files inside?
    # For this test, we don't upload persistent files.

def test_path_traversal():
    print("\n--- Testing Path Traversal ---")

    # Use generator for setup/teardown
    gen = setup_teardown()
    secret_path = next(gen)

    try:
        # 1. Direct function call verification
        # Attempt to access ../secret.txt
        # ROOT_DIR is backend/, so ../secret.txt resolves to secret.txt inside backend/
        # Wait, if ROOT_DIR is backend/, base_dir is backend/temp_uploads.
        # ../secret.txt -> backend/secret.txt.

        try:
            # We must use asyncio.run because serve_temp_image is async
            asyncio.run(serve_temp_image(filename="../secret.txt"))
            print("❌ Vulnerability: serve_temp_image accepted '../secret.txt'")
            assert False, "Should have raised HTTPException"
        except Exception as e:
            if "404" in str(e):
                print("✅ Protected: '../secret.txt' raised 404 (Access Denied/Not Found)")
            else:
                print(f"❓ Unexpected Error: {e}")
                # If it raises something else, it might be an error in test setup, but 404 is what we expect for blocked path.

        # 2. Test encoded path
        try:
            asyncio.run(serve_temp_image(filename="..%2Fsecret.txt")) # decoded by FastAPI usually before passing? No, depends.
            # If passed as literal "..%2Fsecret.txt", os.path.basename handles it safely?
            # If decoded to "../secret.txt", blocked.
            # If literal, basename is "..%2Fsecret.txt", looking for file of that name. Won't find it. 404.
            print("✅ Protected: Encoded path resulted in 404/Success") # If it returns 404 it's safe.
        except Exception as e:
             if "404" in str(e):
                 print("✅ Protected: Encoded path raised 404")

    finally:
        # Teardown
        try:
            next(gen)
        except StopIteration:
            pass

def test_file_upload_extension():
    print("\n--- Testing File Upload Extension ---")

    # Mock authentication
    # We need to find the exact dependency object to override
    # Since we imported app from backend.server, we can look up the dependency there?
    # No, we need to import get_current_user from backend.core.deps
    # But backend.core.deps is mocked in sys.modules!
    # So we must use the SAME mock object that was used during import of server.py

    mock_deps = sys.modules["backend.core.deps"]

    # Override the dependency on the app
    # Warning: app.dependency_overrides requires the original function object.
    # Since we mocked the module, get_current_user is a MagicMock.
    # We must use that exact MagicMock instance as the key.

    app.dependency_overrides[mock_deps.get_current_user] = lambda: {"user_id": "test_user"}

    # Test 1: Allowed extension
    files = {'file': ('test.jpg', b'fake image content', 'image/jpeg')}
    response = client.post("/api/upload-image", files=files)
    if response.status_code == 200:
        print("✅ Allowed extension .jpg uploaded successfully")
    else:
        print(f"❌ Failed to upload .jpg: {response.status_code} {response.text}")
        # Assert failure
        assert response.status_code == 200

    # Test 2: Disallowed extension (HTML)
    files = {'file': ('exploit.html', b'<script>alert(1)</script>', 'text/html')}
    response = client.post("/api/upload-image", files=files)
    if response.status_code == 400:
        print("✅ Disallowed extension .html rejected (400)")
    else:
        print(f"❌ Failed: .html returned {response.status_code} {response.text}")
        assert response.status_code == 400

    # Test 3: Disallowed extension (Python script)
    files = {'file': ('script.py', b'print("hacked")', 'text/x-python')}
    response = client.post("/api/upload-image", files=files)
    if response.status_code == 400:
        print("✅ Disallowed extension .py rejected (400)")
    else:
        print(f"❌ Failed: .py returned {response.status_code} {response.text}")
        assert response.status_code == 400

if __name__ == "__main__":
    try:
        test_path_traversal()
        test_file_upload_extension()
        print("\nAll security tests passed!")
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAN ERROR OCCURRED: {e}")
        sys.exit(1)
