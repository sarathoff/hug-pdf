from fastapi import APIRouter, Response, HTTPException, Depends
from backend.schemas.ai import ConvertToPDFRequest, DownloadPDFRequest
from services.pdf_service import PDFService
from typing import Optional
from backend.core.deps import get_current_user, get_supabase_admin
from services.credit_service import CreditService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


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
async def download_pdf(
    request: DownloadPDFRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    try:
        # Check credits if user is logged in
        if current_user:
            credit_service = CreditService(get_supabase_admin())
            has_credit, msg = credit_service.check_credit_available(current_user['user_id'], 'pdf')
            if not has_credit:
                raise HTTPException(status_code=402, detail=msg)

        pdf_service = PDFService()
        if request.latex_content:
            pdf_bytes = await pdf_service.generate_pdf(request.latex_content)
        elif request.html_content:
             # Fallback
             pdf_bytes = await pdf_service.generate_pdf(request.html_content)
        else:
             raise HTTPException(status_code=400, detail="No content provided")

        # Deduct credits after successful generation
        if current_user:
            credit_service = CreditService(get_supabase_admin())
            credit_service.deduct_credit(current_user['user_id'], 'pdf', "Downloaded PDF document")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
