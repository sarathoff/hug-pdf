from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from pydantic import BaseModel
from backend.schemas.ai import (
    GenerateInitialRequest, GenerateInitialResponse,
    ChatRequest, ChatResponse,
    GeneratePPTRequest, GeneratePPTResponse
)
from services.gemini_service import GeminiService
from services.ppt_generator_service import PPTGeneratorService
from services.auth_service import AuthService
from services.credit_service import CreditService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

from backend.core.deps import get_current_user

# Dependencies (can be moved to a deps.py later)
def get_gemini_service():
    return GeminiService()

def get_ppt_service():
    from services.pexels_service import PexelsService
    return PPTGeneratorService(get_gemini_service(), PexelsService())


@router.post("/generate-initial", response_model=GenerateInitialResponse)
async def generate_initial(
    request: GenerateInitialRequest,
    current_user: Optional[dict] = Depends(get_current_user),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    try:
        # Check credits if user is logged in
        if current_user:
            from backend.core.deps import get_supabase_admin
            credit_service = CreditService(get_supabase_admin())
            # Check if user has credits (will raise 402 if not)
            has_credit, msg = credit_service.check_credit_available(current_user['user_id'], 'pdf')
            if not has_credit:
                raise HTTPException(status_code=402, detail=msg)
            
        result = gemini_service.generate_html_from_prompt(
            request.prompt, 
            mode=request.mode, 
            tier=current_user.get('tier', 'starter') if current_user else 'starter'
        )
        
        # Deduct credits
        if current_user:
             from backend.core.deps import get_supabase_admin
             credit_service = CreditService(get_supabase_admin())
             credit_service.deduct_credit(current_user['user_id'], 'pdf', f"Generated {request.mode} document")
             
        return GenerateInitialResponse(
            session_id="new_session", # In real app, create session in DB
            html_content=result['html'],
            latex_content=result['latex'],
            message=result['message'],
            credits_remaining=10 # fetch actual
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_current_user),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    try:
        result = gemini_service.modify_html(
            request.current_html,
            request.message,
            current_latex=request.current_latex if hasattr(request, 'current_latex') else None,
            mode=request.mode
        )
        return ChatResponse(
            html_content=result['html'],
            latex_content=result['latex'],
            message=result['message']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ModifyLatexRequest(BaseModel):
    session_id: Optional[str] = None
    modification: str
    current_latex: str
    mode: Optional[str] = 'normal'

class ModifyLatexResponse(BaseModel):
    latex_content: str
    html_content: str
    message: str

@router.post("/modify-latex", response_model=ModifyLatexResponse)
async def modify_latex(
    request: ModifyLatexRequest,
    current_user: Optional[dict] = Depends(get_current_user),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    try:
        # Check permissions if mode is research/ebook
        if request.mode in ['research', 'ebook'] and not current_user:
             raise HTTPException(status_code=401, detail="Authentication required")

        result_latex = gemini_service.modify_latex(
            request.current_latex,
            request.modification,
            mode=request.mode
        )
        
        return ModifyLatexResponse(
            latex_content=result_latex,
            html_content=result_latex,
            message="Content updated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
