from fastapi import APIRouter, Response, HTTPException
from backend.schemas.ai import ConvertToPDFRequest
from services.pdf_service import PDFService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

from backend.schemas.ai import DownloadPDFRequest

@router.post("/preview-pdf")
async def preview_pdf(request: DownloadPDFRequest):
    """Generate PDF preview from LaTeX content (no authentication required, fast single-pass)"""
    try:
        pdf_service = PDFService()
        if request.latex_content:
            pdf_bytes = await pdf_service.generate_pdf(request.latex_content, preview_mode=True)
        elif request.html_content:
            pdf_bytes = await pdf_service.generate_pdf(request.html_content, preview_mode=True)
        else:
            raise HTTPException(status_code=400, detail="No content provided")
            
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Type": "application/pdf",
                "Cache-Control": "no-cache"
            }
        )
    except Exception as e:
        logger.error(f"Error in preview_pdf: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download-pdf")
async def download_pdf(request: DownloadPDFRequest):
    try:
        pdf_service = PDFService()
        if request.latex_content:
            pdf_bytes = await pdf_service.generate_pdf(request.latex_content)
        elif request.html_content:
             # Fallback
             pdf_bytes = await pdf_service.generate_pdf(request.html_content)
        else:
             raise HTTPException(status_code=400, detail="No content provided")
             
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename}"
            }
        )
    except Exception as e:
        logger.error(f"PDF Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
