#!/usr/bin/env python3
"""Quick test script to debug chat endpoint error"""

import sys
sys.path.insert(0, 'd:/projects/pdf/backend')

from services.gemini_service import GeminiService

try:
    print("Initializing GeminiService...")
    service = GeminiService()
    
    print("\nTesting modify_latex...")
    result = service.modify_latex(
        current_latex="\\documentclass{article}\\begin{document}Hello\\end{document}",
        modification_request="add a title",
        mode="normal"
    )
    print(f"Success! Result length: {len(result)}")
    print(f"First 100 chars: {result[:100]}")
    
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
