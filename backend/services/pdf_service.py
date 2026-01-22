from io import BytesIO
import logging
import subprocess
import tempfile
import os
import re
import requests
import hashlib
import shutil
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    def _extract_image_urls(latex_content: str) -> list:
        """Extract all image URLs from LaTeX content"""
        # Match \includegraphics{http...} patterns
        pattern = r'\\includegraphics(?:\[.*?\])?\{(https?://[^\}]+)\}'
        urls = re.findall(pattern, latex_content)
        logger.info(f"Found {len(urls)} image URLs in LaTeX")
        return urls

    @staticmethod
    def _download_image(url: str, temp_dir: Path) -> str:
        """Download image from URL to temp directory"""
        try:
            logger.info(f"Downloading image from: {url}")

            # Check if this is a localhost/temp-images URL - copy directly instead of downloading
            if 'localhost' in url or '127.0.0.1' in url:
                if '/temp-images/' in url:
                    filename = url.split('/temp-images/')[-1].split('?')[0]
                    # Construct path to uploaded file
                    from pathlib import Path as PathLib
                    source_path = PathLib(__file__).parent.parent / "temp_uploads" / filename

                    if source_path.exists():
                        # Copy to temp directory
                        dest_path = temp_dir / filename
                        shutil.copy(source_path, dest_path)
                        logger.info(f"Copied local image to: {dest_path}")
                        return str(dest_path)
                    else:
                        logger.error(f"Local image not found: {source_path}")
                        return None

            # For external URLs (Pexels, etc.), download via HTTP
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                # Generate unique filename based on URL hash
                url_hash = hashlib.md5(url.encode()).hexdigest()

                # Try to get extension from URL or content-type
                ext = 'jpg'
                if '.' in url.split('/')[-1].split('?')[0]:
                    ext = url.split('/')[-1].split('?')[0].split('.')[-1]
                elif 'content-type' in response.headers:
                    content_type = response.headers['content-type']
                    if 'png' in content_type:
                        ext = 'png'
                    elif 'jpeg' in content_type or 'jpg' in content_type:
                        ext = 'jpg'

                filename = f"img_{url_hash}.{ext}"
                filepath = temp_dir / filename

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                logger.info(f"Successfully downloaded image to: {filepath}")
                return str(filepath)
            else:
                logger.error(f"Failed to download image from {url}: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error downloading image from {url}: {str(e)}")
            return None

    @staticmethod
    def _replace_urls_with_paths(latex_content: str, url_to_path_map: dict) -> str:
        """Replace image URLs with local file paths in LaTeX"""
        modified_latex = latex_content
        for url, path in url_to_path_map.items():
            if path:
                # Replace backslashes with forward slashes for LaTeX
                latex_path = path.replace('\\', '/')
                modified_latex = modified_latex.replace(url, latex_path)
                logger.info(f"Replaced URL {url} with local path {latex_path}")
        return modified_latex


    @staticmethod
    def _generate_pdf_sync(latex_content: str, preview_mode: bool = False) -> bytes:
        """Synchronous implementation of PDF generation (blocking)"""
        logger.info(f"Starting synchronous PDF generation (preview_mode={preview_mode})")

        # Create a temporary directory for LaTeX compilation
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Step 1: Extract and download images
            image_urls = PDFService._extract_image_urls(latex_content)
            url_to_path_map = {}

            if image_urls:
                logger.info(f"Processing {len(image_urls)} images...")
                for url in image_urls:
                    local_path = PDFService._download_image(url, tmpdir_path)
                    if local_path:
                        url_to_path_map[url] = local_path

                # Replace URLs with local paths
                latex_content = PDFService._replace_urls_with_paths(latex_content, url_to_path_map)

            # Step 2: Write modified LaTeX to file
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

                # Run twice to resolve references (skip for preview mode for speed)
                # Run twice to resolve references (skip for preview mode unless TOC is present)
                # Table of Contents requires a second pass to generate the .toc file and include it
                needs_second_pass = not preview_mode or '\\tableofcontents' in latex_content

                if pdf_file.exists() and needs_second_pass:
                    logger.info("Running pdflatex second time to resolve references/TOC")
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
                elif preview_mode:
                    logger.info("Skipping second pdflatex run (preview mode, no TOC found)")


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

    @staticmethod
    async def generate_pdf(latex_content: str, preview_mode: bool = False) -> bytes:
        """Convert LaTeX to PDF using pdflatex (Non-blocking wrapper)"""
        # Run the synchronous generation in a separate thread to prevent blocking the event loop
        return await asyncio.to_thread(PDFService._generate_pdf_sync, latex_content, preview_mode)
