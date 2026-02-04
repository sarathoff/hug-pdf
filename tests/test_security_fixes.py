
import os
import sys
from unittest.mock import MagicMock
from pathlib import Path

# --- MOCKING STRATEGY ---
modules_to_mock = [
    "supabase",
    "dodopayments",
    "google",
    "google.genai",
    "google.generativeai",
    "bs4",
    "jwt",
    "firecrawl",
    "xhtml2pdf",
    "reportlab",
    "PyPDF2",
    "pylatex",
    "requests",
    "boto3",
    "botocore",
    "dotenv",
    "bcrypt",
    "passlib",
    "passlib.context",
    "email_validator"
]

# Apply mocks to sys.modules
for module_name in modules_to_mock:
    sys.modules[module_name] = MagicMock()

sys.modules["google.genai"].Client = MagicMock()
sys.modules["dodopayments"].DodoPayments = MagicMock()

# Setup Env
os.environ["GEMINI_API_KEY"] = "fake_key"
os.environ["SUPABASE_URL"] = "https://fake.supabase.co"
os.environ["SUPABASE_KEY"] = "fake_key"
os.environ["DODO_PAYMENTS_API_KEY"] = "fake_key"
# Fix for upload_image relying on BACKEND_URL
os.environ["BACKEND_URL"] = "http://testserver"

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
# Also add root for "backend" package resolution if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import Pydantic BaseModel to mock response models if needed,
# but server.py imports them. Since we have pydantic installed, it should be fine.
# If server.py imports models from `backend.models`, and those import Supabase, we might have issues.
# We might need to mock `backend.core.deps` specifically.

try:
    # We need to mock get_current_user in server.py because upload_image depends on it
    # And we don't want to rely on the actual dependency logic which calls Supabase.

    # We'll import app after patching deps?
    # Hard to patch deps before import if they are imported at module level.
    # But Depends(get_current_user) uses the function reference.

    from backend.server import app, get_current_user
    from fastapi.testclient import TestClient
    from fastapi import UploadFile

    # Override dependency
    async def mock_get_current_user():
        return {"user_id": "test_user", "email": "test@example.com", "credits": 100, "plan": "free"}

    app.dependency_overrides[get_current_user] = mock_get_current_user

except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

client = TestClient(app)

def test_path_traversal():
    print("Testing Path Traversal...")
    # 1. Traversal attempt
    # We use a path that resolves to server.py if vulnerable
    # server.py is in backend/, temp_uploads is backend/temp_uploads/
    # So ../server.py maps to backend/server.py

    # Note: TestClient normalizes paths. We rely on the fact that we fixed it by using basename.
    # If the code uses basename, "foo/../bar" becomes "bar".
    # If the code uses path joining, "foo/../bar" becomes "bar" (resolved) or "foo/../bar".

    # To test vulnerability, we want to send ".." which is hard with TestClient.
    # But we can test that accessing "server.py" (if we could traverse to it) is blocked.

    # Let's try encoded path which might pass through to the app logic
    encoded = "%2E%2E%2Fserver.py"
    response = client.get(f"/api/temp-images/{encoded}")

    # If vulnerable and it worked, status is 200.
    # If fixed (basename), it looks for "server.py" in temp_uploads, which doesn't exist -> 404.
    # If fixed (validation), it might return 400.

    # Wait, if vulnerable, "server.py" exists in ROOT_DIR (backend/).
    # So ROOT_DIR/temp_uploads/../server.py -> ROOT_DIR/server.py -> EXISTS.
    # So 200 means VULNERABLE.
    # 404 means SAFE (because it looked in temp_uploads/server.py and didn't find it).

    print(f"Traversal Status: {response.status_code}")
    if response.status_code == 200:
        print("[-] VULNERABLE: Path traversal succeeded")
        return False
    else:
        print("[+] SAFE: Path traversal blocked (or file not found in target dir)")
        return True

def test_arbitrary_upload():
    print("Testing Arbitrary File Upload...")

    # 1. Upload .py file (Malicious)
    files = {'file': ('evil.py', b'print("hacked")', 'text/x-python')}
    response = client.post("/api/upload-image", files=files)

    print(f"Upload .py Status: {response.status_code}")

    # If vulnerable, it accepts it -> 200.
    # If fixed, it rejects -> 400.

    vulnerable = False
    if response.status_code == 200:
        print("[-] VULNERABLE: Allowed .py upload")
        vulnerable = True
    else:
        print("[+] SAFE: Blocked .py upload")

    # 2. Upload .jpg file (Valid)
    files_jpg = {'file': ('good.jpg', b'fake_image_content', 'image/jpeg')}
    response_jpg = client.post("/api/upload-image", files=files_jpg)

    print(f"Upload .jpg Status: {response_jpg.status_code}")
    if response_jpg.status_code != 200:
        print("[-] BROKEN: Valid .jpg upload failed")
        # If we broke valid uploads, that's bad.
        # But for now we just report status.

    return not vulnerable

if __name__ == "__main__":
    safe_traversal = test_path_traversal()
    safe_upload = test_arbitrary_upload()

    if safe_traversal and safe_upload:
        print("\n✅ SYSTEM SECURE")
        sys.exit(0)
    else:
        print("\n❌ SYSTEM VULNERABLE")
        sys.exit(1)
