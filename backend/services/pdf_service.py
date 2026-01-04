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
            
            # Write LaTeX content to file
            tex_file.write_text(latex_content, encoding='utf-8')
            
            try:
                # Try to compile with pdflatex
                # -interaction=nonstopmode: don't stop for errors
                # --enable-installer: allow MiKTeX to install packages
                result = subprocess.run(
                    [
                        'pdflatex', 
                        '-interaction=nonstopmode',
                        '--enable-installer',
                        '-output-directory', str(tmpdir_path), 
                        str(tex_file)
                    ],
                    capture_output=True,
                    text=True,
                    stdin=subprocess.DEVNULL,  # Prevent hanging on input prompts
                    timeout=120,  # Increased to allow package installation
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
                            '--enable-installer',
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
                    logger.error(f"STDOUT: {result.stdout[:1000]}")
                    logger.error(f"STDERR: {result.stderr[:1000]}")
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