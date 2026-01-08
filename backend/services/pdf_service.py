from io import BytesIO
import logging
import subprocess
import tempfile
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    async def generate_pdf(latex_content: str) -> bytes:
        """Convert LaTeX to PDF using pdflatex"""
        
        logger.info("Attempting PDF generation from LaTeX")
        
        # Create a temporary directory for LaTeX compilation
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tex_file = tmpdir_path / "document.tex"
            pdf_file = tmpdir_path / "document.pdf"
            log_file = tmpdir_path / "document.log"
            
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
                    error_details = "LaTeX compilation failed."
                    if log_file.exists():
                        log_content = log_file.read_text(encoding='utf-8', errors='ignore')
                        log_tail = log_content[-1000:]
                        logger.error(f"LaTeX log file (last 2000 chars): {log_content[-2000:]}")
                        error_details += f"\nLog tail:\n{log_tail}"
                    
                    raise Exception(error_details)
                    
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