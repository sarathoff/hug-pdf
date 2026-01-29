import subprocess
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

latex_content = Path("PPT_samples/minimalistic.md").read_text(encoding='utf-8')

print("Starting compilation check for minimalistic.md...")

tmpdir_path = Path("temp_debug_minimalistic")
tmpdir_path.mkdir(exist_ok=True)
tex_file = tmpdir_path / "document.tex"
tex_file.write_text(latex_content, encoding='utf-8')

cmd = [
    'pdflatex',
    '-interaction=nonstopmode',
    '-output-directory', str(tmpdir_path),
    str(tex_file)
]

try:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    
    print(f"Return Code: {result.returncode}")
    print("STDOUT Head:")
    print(result.stdout[:500])
    
    if result.returncode != 0:
        print("\nPossible Error in Log (Tail):")
        log_file = tmpdir_path / "document.log"
        if log_file.exists():
            print(log_file.read_text(encoding='utf-8', errors='ignore')[-1500:])
        else:
            print("No log file found.")
            print("STDERR:")
            print(result.stderr)

except Exception as e:
    print(f"Exception: {e}")
