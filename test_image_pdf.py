import sys
sys.path.append('d:/pdf/backend')

from services.pdf_service import PDFService
import asyncio

# Test LaTeX with image
test_latex = r"""
\documentclass{article}
\usepackage{graphicx}
\begin{document}

\section{Test Document}

This is a test document with an image:

\includegraphics[width=0.5\textwidth]{http://localhost:8000/api/temp-images/b218c9a3-265f-45b7-904a-edbea85f7605.png}

\end{document}
"""

async def test():
    pdf_bytes = await PDFService.generate_pdf(test_latex)
    with open('test_output.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print("PDF generated successfully!")

asyncio.run(test())
