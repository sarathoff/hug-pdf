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
        
        # --- Persist session to Supabase ---
        import uuid
        from datetime import datetime, timezone
        session_id = str(uuid.uuid4())
        title = (request.prompt[:60] + '…') if len(request.prompt) > 60 else request.prompt
        initial_messages = [
            {"role": "user", "content": request.prompt},
            {"role": "assistant", "content": result['message']}
        ]

        if current_user:
            try:
                from backend.core.deps import get_supabase_admin
                supabase = get_supabase_admin()
                supabase.table('sessions').insert({
                    'session_id': session_id,
                    'user_id': current_user['user_id'],
                    'title': title,
                    'messages': initial_messages,
                    'current_latex': result.get('latex', ''),
                    'mode': request.mode or 'normal',
                    'created_at': datetime.now(timezone.utc).isoformat(),
                }).execute()
                logger.info(f"Session {session_id} saved for user {current_user['user_id']}")
            except Exception as db_err:
                logger.warning(f"Failed to save session to DB (non-fatal): {db_err}")

        return GenerateInitialResponse(
            session_id=session_id,
            html_content=result['html'],
            latex_content=result['latex'],
            message=result['message'],
            credits_remaining=10 # fetch actual
        )
    except Exception as e:
        logger.exception(f"Error in generate_initial: {e}")
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

        # --- Update session in Supabase ---
        if current_user and request.session_id and request.session_id != 'new_session':
            try:
                from backend.core.deps import get_supabase_admin
                supabase = get_supabase_admin()
                existing = supabase.table('sessions').select('messages').eq('session_id', request.session_id).execute()
                prev_messages = existing.data[0]['messages'] if existing.data else []
                updated_messages = prev_messages + [
                    {"role": "user", "content": request.message},
                    {"role": "assistant", "content": result['message']}
                ]
                supabase.table('sessions').update({
                    'messages': updated_messages,
                    'current_latex': result.get('latex', ''),
                }).eq('session_id', request.session_id).execute()
            except Exception as db_err:
                logger.warning(f"Failed to update session {request.session_id} (non-fatal): {db_err}")

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
