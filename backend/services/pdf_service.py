from playwright.async_api import async_playwright
from io import BytesIO
import logging
import weasyprint

logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    async def generate_pdf(html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint as primary method, Playwright as fallback"""
        try:
            # Try WeasyPrint first (more reliable in containers)
            logger.info("Attempting PDF generation with WeasyPrint")
            html_doc = weasyprint.HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf()
            logger.info("Successfully generated PDF using WeasyPrint")
            return pdf_bytes
            
        except Exception as weasy_error:
            logger.warning(f"WeasyPrint PDF generation failed: {weasy_error}")
            
            # Fallback to Playwright
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
                        
            except Exception as playwright_error:
                logger.error(f"All PDF generation methods failed. WeasyPrint: {weasy_error}, Playwright: {playwright_error}")
                raise Exception(f"PDF generation failed: {playwright_error}")
                
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise