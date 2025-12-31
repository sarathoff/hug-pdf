from playwright.async_api import async_playwright
from io import BytesIO
import logging

# Try to import weasyprint, but don't fail if it's not available
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    logging.warning(f"WeasyPrint not available: {e}")

logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    async def generate_pdf(html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint as primary method, Playwright as fallback"""
        
        # Try WeasyPrint first if available
        if WEASYPRINT_AVAILABLE:
            try:
                logger.info("Attempting PDF generation with WeasyPrint")
                html_doc = weasyprint.HTML(string=html_content)
                pdf_bytes = html_doc.write_pdf()
                logger.info("Successfully generated PDF using WeasyPrint")
                return pdf_bytes
            except Exception as weasy_error:
                logger.warning(f"WeasyPrint PDF generation failed: {weasy_error}")
        
        # Use Playwright as fallback
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set content
                await page.set_content(html_content, wait_until='networkidle')
                
                # Generate PDF
                pdf_bytes = await page.pdf(
                    format='A4',
                    print_background=True,
                    margin={'top': '0.5in', 'right': '0.5in', 'bottom': '0.5in', 'left': '0.5in'}
                )
                
                await browser.close()
                logger.info("Successfully generated PDF using Playwright")
                return pdf_bytes
                
        except Exception as playwright_error:
            logger.error(f"Playwright PDF generation failed: {playwright_error}")
            raise Exception(f"PDF generation failed: {playwright_error}")
                
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise