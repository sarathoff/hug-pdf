import sys
import os
import pytest
from pathlib import Path
from fastapi import HTTPException

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

# Mock environment variables
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy_key"
os.environ["DODO_PAYMENTS_API_KEY"] = "dummy_dodo"
os.environ["GEMINI_API_KEY"] = "dummy_gemini"

try:
    from server import serve_temp_image, ROOT_DIR
except ImportError as e:
    pytest.fail(f"Failed to import server app: {e}")

# We need asyncio loop to run async function
import asyncio

def run_async(coro):
    return asyncio.run(coro)

def test_path_traversal_vulnerability():
    """
    Test that path traversal attempts are detected.
    """
    # 1. Create a dummy file in the temp_uploads directory
    temp_dir = ROOT_DIR / "temp_uploads"
    temp_dir.mkdir(exist_ok=True)

    safe_filename = "safe_image.txt"
    safe_filepath = temp_dir / safe_filename
    with open(safe_filepath, "w") as f:
        f.write("safe content")

    # 2. Verify normal access works
    try:
        response = run_async(serve_temp_image(safe_filename))
        # It returns a FileResponse
        print(f"DEBUG: response.path: {response.path}")
        print(f"DEBUG: safe_filepath: {safe_filepath}")

        # Compare resolved paths to avoid relative vs absolute mismatch
        assert Path(response.path).resolve() == safe_filepath.resolve()
        print(f"Normal access passed: {response.path}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        pytest.fail(f"Normal access failed: {e}")

    # 3. Attempt path traversal to read requirements.txt
    traversal_filename = "../requirements.txt"

    # In vulnerable state, this returns the file path to requirements.txt
    # In fixed state, it should raise HTTPException(404) or similar.

    try:
        response = run_async(serve_temp_image(traversal_filename))

        # If we reach here, it returned a response (VULNERABLE)
        print(f"Traversed path: {response.path}")

        # Verify it actually resolved to outside directory
        resolved_path = Path(response.path).resolve()
        expected_root = (ROOT_DIR / "temp_uploads").resolve()

        if not resolved_path.is_relative_to(expected_root):
            pytest.fail(f"VULNERABILITY DETECTED: Served file outside temp_uploads: {resolved_path}")

    except HTTPException as e:
        # If it raises 404/403, it might be because file doesn't exist (404) or blocked (403).
        # In current vulnerable code:
        # filepath = ROOT_DIR / "temp_uploads" / filename
        # if not filepath.exists(): raise 404
        # Since ../requirements.txt exists, it should NOT raise 404.

        # If we fix it to raise 403, we are good.
        print(f"Caught expected exception (if fixed): {e}")

    # Clean up
    if safe_filepath.exists():
        safe_filepath.unlink()

if __name__ == "__main__":
    try:
        test_path_traversal_vulnerability()
        print("Tests finished")
    except Exception as e:
        print(f"Tests ERROR: {e}")
        sys.exit(1)
