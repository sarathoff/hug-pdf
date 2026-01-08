from io import BytesIO
import logging
import subprocess
import tempfile
import os
from pathlib import Path

# Try to import xhtml2pdf for HTML fallback
try:
    from xhtml2pdf import pisa
    HTML_TO_PDF_AVAILABLE = True
except ImportError:
    HTML_TO_PDF_AVAILABLE = False
    logging.warning("xhtml2pdf not installed. HTML to PDF fallback will not work.")

logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    def is_latex_available() -> bool:
        """Check if pdflatex is installed and available"""
        from shutil import which
        return which('pdflatex') is not None

    @staticmethod
    async def generate_pdf_from_html(html_content: str) -> bytes:
        """Convert HTML to PDF using xhtml2pdf as fallback"""
        if not HTML_TO_PDF_AVAILABLE:
            raise Exception("HTML to PDF generation failed: xhtml2pdf not installed.")

        logger.info("Attempting PDF generation from HTML (Fallback)")

        # Create a PDF buffer
        pdf_buffer = BytesIO()

        try:
            # Convert HTML to PDF
            pisa_status = pisa.CreatePDF(
                html_content,                # the HTML to convert
                dest=pdf_buffer             # file handle to recieve result
            )

            if pisa_status.err:
                raise Exception(f"xhtml2pdf error: {pisa_status.err}")

            pdf_bytes = pdf_buffer.getvalue()
            logger.info(f"Successfully generated PDF from HTML ({len(pdf_bytes)} bytes)")
            return pdf_bytes

        except Exception as e:
            logger.error(f"HTML to PDF conversion error: {str(e)}")
            raise Exception(f"PDF generation from HTML failed: {str(e)}")

    @staticmethod
    async def generate_pdf(latex_content: str) -> bytes:
        """Convert LaTeX to PDF using pdflatex"""

        logger.info("Attempting PDF generation from LaTeX")

        # Create a temporary directory for LaTeX compilation
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tex_file = tmpdir_path / "document.tex"
            pdf_file = tmpdir_path / "document.pdf"

            # Write LaTeX content to file
            tex_file.write_text(latex_content, encoding='utf-8')

            try:
                # Try to compile with pdflatex
                # -interaction=nonstopmode: don't stop for errors
                result = subprocess.run(
                    [
                        'pdflatex',
                        '-interaction=nonstopmode',
                        '-output-directory', str(tmpdir_path),
                        str(tex_file)
                    ],
                    capture_output=True,
                    text=True,
                    stdin=subprocess.DEVNULL,  # Prevent hanging on input prompts
                    timeout=120,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )

                logger.info(f"First pdflatex run completed with return code: {result.returncode}")

                # Run twice to resolve references (only if first run succeeded)
                if pdf_file.exists():
                    logger.info("Running pdflatex second time to resolve references")
                    subprocess.run(
                        [
                            'pdflatex',
                            '-interaction=nonstopmode',
                            '-output-directory', str(tmpdir_path),
                            str(tex_file)
                        ],
                        capture_output=True,
                        text=True,
                        stdin=subprocess.DEVNULL,
                        timeout=120,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )

                if pdf_file.exists():
                    pdf_bytes = pdf_file.read_bytes()
                    logger.info(f"Successfully generated PDF from LaTeX ({len(pdf_bytes)} bytes)")
                    return pdf_bytes
                else:
                    logger.error(f"pdflatex failed to create PDF.")
                    logger.error(f"Return code: {result.returncode}")
                    logger.error(f"STDOUT (full): {result.stdout}")
                    logger.error(f"STDERR (full): {result.stderr}")
                    logger.error(f"LaTeX content (first 500 chars): {latex_content[:500]}")

                    # Check if .log file exists for more details
                    log_file = tmpdir_path / "document.log"
                    if log_file.exists():
                        log_content = log_file.read_text(encoding='utf-8', errors='ignore')
                        logger.error(f"LaTeX log file (last 2000 chars): {log_content[-2000:]}")

                    raise Exception(f"LaTeX compilation failed. Check the LaTeX syntax and ensure all required packages are installed.")

            except FileNotFoundError:
                logger.error("pdflatex not found. Please install a TeX distribution (MiKTeX or TeX Live)")
                raise Exception("PDF generation failed: pdflatex not installed. Please install MiKTeX or TeX Live.")
            except subprocess.TimeoutExpired:
                logger.error("LaTeX compilation timed out. This may be due to MiKTeX trying to install packages.")
                logger.error("Please install required LaTeX packages manually or enable automatic package installation in MiKTeX.")
                raise Exception("PDF generation timed out. Please ensure all LaTeX packages are installed.")
            except Exception as e:
                logger.error(f"LaTeX compilation error: {str(e)}")
                raise Exception(f"PDF generation failed: {str(e)}")
