import sys
import os
from pathlib import Path
from unittest.mock import MagicMock
import asyncio

# Set up paths
BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.append(str(BACKEND_DIR))

# Mock environment variables
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "mock-key"
os.environ["GEMINI_API_KEY"] = "mock-key"
os.environ["DODO_PAYMENTS_API_KEY"] = "mock-key"
os.environ["PAYMENT_TEST_MODE"] = "true"

# Mock dependencies
sys.modules["supabase"] = MagicMock()
sys.modules["dodopayments"] = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["google.api_core"] = MagicMock()
sys.modules["google.auth"] = MagicMock()
sys.modules["bs4"] = MagicMock()
sys.modules["firecrawl"] = MagicMock()
sys.modules["PyPDF2"] = MagicMock()
sys.modules["pylatex"] = MagicMock()
sys.modules["xhtml2pdf"] = MagicMock()
sys.modules["weasyprint"] = MagicMock()

# Import serve_temp_image directly
try:
    from server import serve_temp_image, ROOT_DIR
    from fastapi import HTTPException
    from fastapi.responses import FileResponse
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def test_path_traversal():
    print("Testing Path Traversal Vulnerability via Direct Function Call...")

    # create a dummy file in temp_uploads
    temp_dir = ROOT_DIR / "temp_uploads"
    temp_dir.mkdir(exist_ok=True)
    with open(temp_dir / "safe.txt", "w") as f:
        f.write("safe content")

    # Test 1: Normal access
    print("\nTest 1: Normal access (safe.txt)")
    try:
        response = await serve_temp_image("safe.txt")
        print(f"✅ Success: Got {type(response)}")
        if isinstance(response, FileResponse):
            print(f"Path: {response.path}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 2: Path Traversal (../server.py)
    print("\nTest 2: Path Traversal (../server.py)")
    try:
        response = await serve_temp_image("../server.py")
        if isinstance(response, FileResponse):
            print("🚨 VULNERABILITY CONFIRMED: Function returned FileResponse for ../server.py")
            print(f"Leaked Path: {response.path}")

            # Verify the path points to server.py
            resolved_path = Path(response.path).resolve()
            if resolved_path.name == "server.py":
                 print("✅ Verified: Path resolves to server.py")
            else:
                 print(f"❓ Unexpected resolution: {resolved_path}")

    except HTTPException as e:
        print(f"✅ Blocked (HTTPException {e.status_code}): {e.detail}")
    except Exception as e:
        print(f"❓ Unexpected error: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_path_traversal())
    loop.close()
