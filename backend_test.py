#!/usr/bin/env python3
"""
Backend API Testing for PDF Generator
Tests the three main endpoints: generate-initial, chat, and download-pdf
"""

import requests
import json
import os
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFGeneratorTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.base_url = self._get_backend_url()
        self.session_id = None
        self.html_content = None
        
    def _get_backend_url(self) -> str:
        """Read backend URL from frontend .env file"""
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        url = line.split('=', 1)[1].strip()
                        return f"{url}/api"
        except Exception as e:
            logger.error(f"Could not read backend URL from .env: {e}")
            return "http://localhost:8001/api"  # fallback
    
    def test_generate_initial(self) -> bool:
        """Test POST /api/generate-initial endpoint"""
        logger.info("Testing POST /api/generate-initial endpoint...")
        
        url = f"{self.base_url}/generate-initial"
        payload = {
            "prompt": "Create a simple business letter"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Expected status 200, got {response.status_code}")
                logger.error(f"Response text: {response.text}")
                return False
            
            data = response.json()
            logger.info(f"Response keys: {list(data.keys())}")
            
            # Verify required fields
            required_fields = ['session_id', 'html_content', 'message']
            for field in required_fields:
                if field not in data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Store session_id and html_content for next tests
            self.session_id = data['session_id']
            self.html_content = data['html_content']
            
            # Verify html_content contains valid HTML
            html = data['html_content']
            if not html or not isinstance(html, str):
                logger.error("html_content is empty or not a string")
                return False
            
            # Basic HTML validation
            html_lower = html.lower()
            if not all(tag in html_lower for tag in ['<html', '<head', '<body']):
                logger.error("html_content does not contain basic HTML structure")
                logger.info(f"HTML preview: {html[:200]}...")
                return False
            
            logger.info("✅ generate-initial test PASSED")
            logger.info(f"Session ID: {self.session_id}")
            logger.info(f"HTML length: {len(html)} characters")
            logger.info(f"Message: {data['message']}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def test_chat(self) -> bool:
        """Test POST /api/chat endpoint"""
        logger.info("Testing POST /api/chat endpoint...")
        
        if not self.session_id or not self.html_content:
            logger.error("Cannot test chat without session_id and html_content from generate-initial")
            return False
        
        url = f"{self.base_url}/chat"
        payload = {
            "session_id": self.session_id,
            "message": "Make it more formal",
            "current_html": self.html_content
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Expected status 200, got {response.status_code}")
                logger.error(f"Response text: {response.text}")
                return False
            
            data = response.json()
            logger.info(f"Response keys: {list(data.keys())}")
            
            # Verify required fields
            required_fields = ['html_content', 'message']
            for field in required_fields:
                if field not in data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Update html_content for PDF test
            self.html_content = data['html_content']
            
            # Verify html_content is valid
            html = data['html_content']
            if not html or not isinstance(html, str):
                logger.error("html_content is empty or not a string")
                return False
            
            # Basic HTML validation
            html_lower = html.lower()
            if not all(tag in html_lower for tag in ['<html', '<head', '<body']):
                logger.error("html_content does not contain basic HTML structure")
                return False
            
            logger.info("✅ chat test PASSED")
            logger.info(f"Updated HTML length: {len(html)} characters")
            logger.info(f"Message: {data['message']}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def test_download_pdf(self) -> bool:
        """Test POST /api/download-pdf endpoint"""
        logger.info("Testing POST /api/download-pdf endpoint...")
        
        if not self.html_content:
            logger.error("Cannot test download-pdf without html_content from previous tests")
            return False
        
        url = f"{self.base_url}/download-pdf"
        payload = {
            "html_content": self.html_content,
            "filename": "test_document.pdf"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)  # Longer timeout for PDF generation
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Expected status 200, got {response.status_code}")
                logger.error(f"Response text: {response.text}")
                return False
            
            # Verify Content-Type header
            content_type = response.headers.get('Content-Type', '')
            if content_type != 'application/pdf':
                logger.error(f"Expected Content-Type 'application/pdf', got '{content_type}'")
                return False
            
            # Verify Content-Disposition header exists
            content_disposition = response.headers.get('Content-Disposition', '')
            if not content_disposition:
                logger.error("Missing Content-Disposition header")
                return False
            
            if 'attachment' not in content_disposition:
                logger.error(f"Content-Disposition should contain 'attachment', got '{content_disposition}'")
                return False
            
            # Verify response is a PDF file (check PDF magic bytes)
            pdf_content = response.content
            if not pdf_content.startswith(b'%PDF-'):
                logger.error("Response content does not appear to be a valid PDF file")
                return False
            
            logger.info("✅ download-pdf test PASSED")
            logger.info(f"PDF size: {len(pdf_content)} bytes")
            logger.info(f"Content-Type: {content_type}")
            logger.info(f"Content-Disposition: {content_disposition}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def test_api_health(self) -> bool:
        """Test basic API health check"""
        logger.info("Testing API health check...")
        
        url = f"{self.base_url}/"
        
        try:
            response = requests.get(url, timeout=10)
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Expected status 200, got {response.status_code}")
                return False
            
            data = response.json()
            if 'message' not in data:
                logger.error("Health check response missing 'message' field")
                return False
            
            logger.info("✅ API health check PASSED")
            logger.info(f"Health message: {data['message']}")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        logger.info(f"Starting PDF Generator API tests...")
        logger.info(f"Backend URL: {self.base_url}")
        
        results = {}
        
        # Test 1: API Health Check
        results['health_check'] = self.test_api_health()
        
        # Test 2: Generate Initial HTML
        results['generate_initial'] = self.test_generate_initial()
        
        # Test 3: Chat (modify HTML) - only if generate_initial passed
        if results['generate_initial']:
            results['chat'] = self.test_chat()
        else:
            results['chat'] = False
            logger.warning("Skipping chat test due to generate_initial failure")
        
        # Test 4: Download PDF - only if previous tests passed
        if results['generate_initial'] and results['chat']:
            results['download_pdf'] = self.test_download_pdf()
        else:
            results['download_pdf'] = False
            logger.warning("Skipping download_pdf test due to previous failures")
        
        return results

def main():
    """Main test execution"""
    tester = PDFGeneratorTester()
    results = tester.run_all_tests()
    
    # Print summary
    print("\n" + "="*60)
    print("PDF GENERATOR API TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests PASSED!")
        return 0
    else:
        print("⚠️  Some tests FAILED!")
        return 1

if __name__ == "__main__":
    exit(main())