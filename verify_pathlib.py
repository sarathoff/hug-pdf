from pathlib import Path
import os

ROOT_DIR = Path("/app/backend")

def check_path(filename):
    filepath = ROOT_DIR / "temp_uploads" / filename
    print(f"Filename: {filename}")
    print(f"Resulting path: {filepath}")
    print(f"Is absolute: {filepath.is_absolute()}")
    try:
        resolved = filepath.resolve()
        print(f"Resolved path: {resolved}")
        print(f"Is relative to ROOT_DIR: {resolved.is_relative_to(ROOT_DIR)}")
    except Exception as e:
        print(f"Resolve error: {e}")
    print("-" * 20)

check_path("test.jpg")
check_path("../server.py")
check_path("/etc/passwd")
