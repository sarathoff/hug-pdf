from playwright.async_api import async_playwright
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    async def generate_pdf(html_content: str) -> bytes:
        """Convert HTML to PDF using Playwright and return as bytes"""
        try:
            async with async_playwright() as p:
                # Try Firefox first as it has better ARM64 support
                try:
                    browser = await p.firefox.launch(headless=True)
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
                    logger.info("Successfully generated PDF using Firefox")
                    return pdf_bytes
                    
                except Exception as firefox_error:
                    logger.warning(f"Firefox PDF generation failed: {firefox_error}")
                    
                    # Fallback to Chromium with explicit headless mode
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
                    logger.info("Successfully generated PDF using Chromium")
                    return pdf_bytes
                
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise