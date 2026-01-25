import os
import logging
from typing import Dict, Optional
import PyPDF2
from io import BytesIO

logger = logging.getLogger(__name__)

class PDFExtractorService:
    """Service for extracting text content from PDF files"""
    
    def extract_text_from_pdf(self, pdf_file) -> Optional[str]:
        """
        Extract text content from uploaded PDF file
        
        Args:
            pdf_file: File object or bytes
            
        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            # Handle both file objects and bytes
            if isinstance(pdf_file, bytes):
                pdf_bytes = BytesIO(pdf_file)
            else:
                pdf_bytes = BytesIO(pdf_file.read())
            
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(pdf_bytes)
            
            # Extract text from all pages
            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
            
            full_text = "\n\n".join(text_content)
            
            if not full_text.strip():
                logger.error("No text content extracted from PDF")
                return None
            
            logger.info(f"Extracted {len(full_text)} characters from PDF ({len(pdf_reader.pages)} pages)")
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return None
    
    def validate_pdf(self, pdf_file) -> bool:
        """
        Validate if file is a valid PDF
        
        Args:
            pdf_file: File object or bytes
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            if isinstance(pdf_file, bytes):
                pdf_bytes = BytesIO(pdf_file)
            else:
                pdf_bytes = BytesIO(pdf_file.read())
                pdf_file.seek(0)  # Reset file pointer
            
            PyPDF2.PdfReader(pdf_bytes)
            return True
        except Exception as e:
            logger.error(f"PDF validation failed: {str(e)}")
            return False
