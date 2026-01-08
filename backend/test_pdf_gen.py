import asyncio
import os
import sys
from services.pdf_service import PDFService

# Create a dummy service instance
service = PDFService()

async def test():
    latex_content = r"""
\documentclass{article}
\begin{document}
Hello World from Python!
\end{document}
"""
    print("Testing PDF Generation with simple content...")
    try:
        pdf_bytes = await service.generate_pdf(latex_content)
        print(f"Success! Generated {len(pdf_bytes)} bytes.")
        with open("test_output.pdf", "wb") as f:
            f.write(pdf_bytes)
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    # Add parent directory to path so we can import services
    sys.path.append(os.getcwd())
    asyncio.run(test())
