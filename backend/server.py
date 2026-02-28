from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends, UploadFile, File
from fastapi.responses import Response, FileResponse
from starlette.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
import sys

# PATH HACK: Ensure consistent imports during refactor
# Add project root to allow 'from backend...'
sys.path.append(str(Path(__file__).parent.parent))
# Add backend dir to allow 'from services...' if running from root
sys.path.append(str(Path(__file__).parent))

# --- New Architecture Imports ---
from backend.core.config import settings
from backend.core.deps import get_current_user, get_supabase_admin, get_supabase_client
from backend.routers import ai, pdf
from backend.schemas.common import StatusCheck, StatusCheckCreate, PurchaseRequest
from backend.schemas.ai import (
    ConvertToPDFRequest, ConvertToPDFResponse,
    OptimizeResumeResponse,
    GeneratePPTRequest, GeneratePPTResponse,
    DownloadPDFRequest # Legacy support if needed
)
from backend.models.user import UserResponse

# Services
from backend.services.payment_service import PaymentService
from backend.services.pexels_service import PexelsService
# Removed RephrasyService
from backend.services.content_converter_service import ContentConverterService
from backend.services.pdf_extractor_service import PDFExtractorService
from backend.services.resume_optimizer_service import ResumeOptimizerService
from backend.services.ppt_generator_service import PPTGeneratorService
from backend.services.gemini_service import GeminiService # For PPT service init
from backend.services.speech_service import get_speech_service
from backend.services.api_key_service import get_api_key_service
from backend.services.rate_limiter_service import get_rate_limiter

# Initialize Logging
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent

# --- API Authentication Dependency ---
async def verify_api_key(authorization: str = Header(None)):
    """
    Verify API key from Authorization header
    Format: Authorization: Bearer pdf_xxxxx
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    
    # Get services
    supabase = get_supabase_admin()
    api_key_service = get_api_key_service(supabase)
    rate_limiter = get_rate_limiter()
    
    # Validate API key
    key_data = api_key_service.validate_api_key(api_key)
    if not key_data:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    
    # Check rate limits
    rate_limit_result = rate_limiter.check_limit(
        key_id=key_data['id'],
        tier=key_data['tier'],
        requests_count=key_data['requests_count'],
        requests_limit=key_data['requests_limit']
    )
    
    if not rate_limit_result['allowed']:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. {rate_limit_result.get('reason', '')}",
            headers={
                "X-RateLimit-Limit": str(rate_limit_result['limit']),
                "X-RateLimit-Remaining": str(rate_limit_result['remaining']),
                "X-RateLimit-Reset": rate_limit_result['reset_at'],
                "Retry-After": str(rate_limit_result.get('retry_after', 60))
            }
        )
    
    # Add rate limit headers to response context
    key_data['rate_limit'] = rate_limit_result
    return key_data

# --- Service Initialization ---
# (Note: AI and PDF services are now initialized within their routers or dependencies)
# But we keep these for the legacy/unmoved endpoints
payment_service = PaymentService()
pexels_service = PexelsService()
# rephrasy_service = RephrasyService()
content_converter_service = ContentConverterService()
pdf_extractor_service = PDFExtractorService()
resume_optimizer_service = ResumeOptimizerService()
# PPT Service needs gemini. We create a fresh instance or use singleton if we had one.
ppt_generator_service = PPTGeneratorService(GeminiService(), pexels_service)

# Dodo Payment Client (Legacy/For Checkout)
from dodopayments import DodoPayments
try:
    dodo_client = DodoPayments(bearer_token=settings.DODO_PAYMENTS_API_KEY)
except Exception as e:
    logger.warning(f"Failed to initialize Dodo Client: {e}")
    dodo_client = None

# --- App Setup ---
app = FastAPI(title="HugPDF API", version="2.0.0")

# CORS - Relaxed for API access
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False, # Must be False when allow_origins=["*"]
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
# AI and PDF endpoints (Refactored)
app.include_router(ai.router, prefix="/api", tags=["AI"])
app.include_router(pdf.router, prefix="/api", tags=["PDF"])

# --- Legacy/Unmoved Routes (Main API Router) ---
api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def root():
    return {"message": "HugPDF API - Ready", "version": "2.0.0"}

# Authentication
@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return UserResponse(
        user_id=current_user['user_id'],
        email=current_user['email'],
        credits=current_user['credits'],
        plan=current_user['plan'],
        early_adopter=current_user.get('early_adopter', False)
    )

# Images (Pexels)
@api_router.get("/images/search")
async def search_images(query: str, per_page: int = 15, page: int = 1):
    try:
        return pexels_service.search_images(query, per_page, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/images/curated")
async def get_curated_images(per_page: int = 15, page: int = 1):
    try:
        return pexels_service.get_curated_images(per_page, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/upload-image")
async def upload_image(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        temp_dir = ROOT_DIR / "temp_uploads"
        temp_dir.mkdir(exist_ok=True)
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_name = f"{uuid.uuid4()}.{file_ext}"
        filepath = temp_dir / unique_name
        content = await file.read()
        with open(filepath, 'wb') as f:
            f.write(content)
        backend_url = os.environ.get('BACKEND_URL', 'http://localhost:8000')
        return {"url": f"{backend_url}/api/temp-images/{unique_name}", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/temp-images/{filename}")
async def serve_temp_image(filename: str):
    filepath = ROOT_DIR / "temp_uploads" / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(filepath)

# Tools: Converter, Resume, Rephrasy
@api_router.post("/convert-to-pdf", response_model=ConvertToPDFResponse)
async def convert_to_pdf(request: ConvertToPDFRequest, current_user: dict = Depends(get_current_user)):
    try:
        if not content_converter_service.validate_url(request.url):
             raise HTTPException(status_code=400, detail="Invalid URL")
        result = content_converter_service.convert_to_pdf(request.url, request.conversion_type, request.options or {})
        if not result: raise HTTPException(status_code=400, detail="Conversion failed")
        return ConvertToPDFResponse(
            latex_content=result['latex'],
            message=result['message'],
            metadata=result.get('metadata', {}),
            conversion_type=result['conversion_type']
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/optimize-resume", response_model=OptimizeResumeResponse)
async def optimize_resume(resume_pdf: UploadFile = File(...), job_description: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    try:
        pdf_content = await resume_pdf.read()
        resume_text = pdf_extractor_service.extract_text_from_pdf(pdf_content)
        result = resume_optimizer_service.optimize_resume(resume_text, job_description)
        if not result: raise HTTPException(status_code=500, detail="Optimization failed")
        return OptimizeResumeResponse(
            latex_content=result['latex'],
            ats_score=result['ats_score'],
            improvements=result['improvements'],
            message=result['message']
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/transcribe-audio")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = "auto",
    current_user: dict = Depends(get_current_user)
):
    """
    Transcribe audio to text using Google Cloud Speech-to-Text API
    
    Args:
        audio: Audio file (WebM, WAV, MP3)
        language: Language code (e.g., 'en-US', 'es-ES') or 'auto' for auto-detection
        current_user: Authenticated user
    
    Returns:
        JSON with transcribed text and detected language
    """
    try:
        if not settings.GOOGLE_CLOUD_CREDENTIALS_PATH or not os.path.isfile(settings.GOOGLE_CLOUD_CREDENTIALS_PATH):
            raise HTTPException(
                status_code=500, 
                detail="Speech-to-Text credentials not configured. Please add google-credentials.json file to the backend directory."
            )
        
        # Read audio content
        audio_content = await audio.read()
        
        # Determine audio encoding from filename
        filename = audio.filename.lower()
        if filename.endswith('.webm'):
            encoding = "WEBM_OPUS"
        elif filename.endswith('.wav'):
            encoding = "LINEAR16"
        elif filename.endswith('.mp3'):
            encoding = "MP3"
        elif filename.endswith('.ogg'):
            encoding = "OGG_OPUS"
        else:
            encoding = "WEBM_OPUS"  # Default
        
        # Get speech service and transcribe
        speech_service = get_speech_service(settings.GOOGLE_CLOUD_CREDENTIALS_PATH)
        result = speech_service.transcribe_audio(
            audio_content=audio_content,
            language_code=language or "auto",
            audio_encoding=encoding
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "success": True,
            "text": result['text'],
            "language": result['language'],
            "message": "Audio transcribed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

# ============================================================================
# API v1 Endpoints - Developer API
# ============================================================================

# --- API Key Management ---

@api_router.post("/v1/keys")
async def create_api_key(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Generate a new API key for the authenticated user"""
    try:
        # Check if user is authenticated
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        supabase = get_supabase_admin()
        api_key_service = get_api_key_service(supabase)
        
        name = request.get('name', 'My API Key')
        tier = request.get('tier', 'free')  # Default to free tier
        
        # Always use 'user_id' (Supabase Auth UUID), NOT 'id' (users table internal PK)
        # current_user is a row from the users table: {id (internal PK), user_id (auth UUID), ...}
        user_id = current_user.get('user_id')
        if not user_id:
            raise HTTPException(status_code=500, detail="User ID not found in token")
        
        result = api_key_service.generate_api_key(
            user_id=user_id,
            name=name,
            tier=tier
        )
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/v1/keys")
async def list_api_keys(current_user: dict = Depends(get_current_user)):
    """List all API keys for the authenticated user"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        supabase = get_supabase_admin()
        api_key_service = get_api_key_service(supabase)
        
        user_id = current_user.get('user_id')  # Auth UUID, not internal PK
        keys = api_key_service.get_user_api_keys(user_id)
        return {"keys": keys}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/v1/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Revoke an API key"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        supabase = get_supabase_admin()
        api_key_service = get_api_key_service(supabase)
        
        user_id = current_user.get('user_id')  # Auth UUID, not internal PK
        success = api_key_service.revoke_api_key(key_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="API key not found")
        
        return {"success": True, "message": "API key revoked"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Direct PDF Generation API ---

@api_router.post("/v1/generate")
async def generate_pdf_api(
    request: dict,
    key_data: dict = Depends(verify_api_key)
):
    """
    Generate PDF and return file directly
    
    Uses the same credit system as the web app - 1 credit per PDF.
    
    Request body:
    {
        "prompt": "Create a resume for John Doe",
        "mode": "normal",  // optional: "normal", "research", "ebook"
        "format": "A4"     // optional
    }
    
    Returns: PDF file (binary)
    """
    try:
        from backend.services.gemini_service import GeminiService
        from backend.services.pdf_service import PDFService
        
        prompt = request.get('prompt')
        if not prompt:
            raise HTTPException(status_code=400, detail="Missing 'prompt' in request body")
        
        mode = request.get('mode', 'normal')
        user_id = key_data.get('user_id')
        
        # Get Supabase client
        supabase = get_supabase_admin()
        
        # Check user credits — use list select (avoid .single() which throws PGRST116 on 0 rows)
        logger.info(f"Looking up user in 'users' table with user_id={user_id}")
        user_response = supabase.table('users').select('credits, plan').eq('user_id', user_id).execute()
        
        # Fallback for legacy API keys that stored the internal 'id' instead of 'user_id'
        if not user_response.data or len(user_response.data) == 0:
            logger.info(f"User not found by user_id, trying fallback lookup by internal id={user_id}")
            user_response = supabase.table('users').select('credits, plan').eq('id', user_id).execute()

        if not user_response.data or len(user_response.data) == 0:
            logger.error(f"User not found in 'users' table for user_id/id={user_id}. This API key may reference a user that doesn't exist.")
            raise HTTPException(status_code=401, detail=f"Unauthorized: Invalid user account associated with this API key. Please generate a new key.")
        
        user_credits = user_response.data[0].get('credits', 0)
        user_plan = user_response.data[0].get('plan', 'free')
        
        # Check if user has credits
        if user_credits < 1:
            raise HTTPException(
                status_code=402, 
                detail="Insufficient credits. Please purchase more credits to continue using the API."
            )
        
        # Determine tier based on plan
        # Credit topup buyers use Flash (sustainable cost). Only subscription plans get Pro model.
        tier = 'pro' if user_plan in ['pro', 'on_demand'] else 'free'
        
        # Initialize services
        gemini_service = GeminiService()
        pdf_service = PDFService()
        
        # Generate LaTeX code
        logger.info(f"Generating PDF for API key {key_data['id']}, user {user_id}: {prompt[:50]}...")
        latex_code = gemini_service.generate_latex_from_prompt(prompt, mode=mode, tier=tier)
        
        # Compile to PDF
        pdf_bytes = await pdf_service.generate_pdf(latex_code)
        
        # Deduct 1 credit from user
        new_credits = user_credits - 1
        supabase.table('users').update({
            'credits': new_credits,
            'updated_at': datetime.now().isoformat()
        }).eq('user_id', user_id).execute()
        
        logger.info(f"PDF generated successfully. Credits remaining: {new_credits}")
        
        # Track usage
        api_key_service = get_api_key_service(supabase)
        api_key_service.track_usage(key_data['id'], '/v1/generate', 200)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"document_{timestamp}.pdf"
        
        # Return PDF with rate limit and credit headers
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-RateLimit-Limit": str(key_data['rate_limit']['limit']),
                "X-RateLimit-Remaining": str(key_data['rate_limit']['remaining']),
                "X-RateLimit-Reset": key_data['rate_limit']['reset_at'],
                "X-Credits-Remaining": str(new_credits)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF generation error: {e}", exc_info=True)
        
        # Track failed usage
        try:
            supabase = get_supabase_admin()
            api_key_service = get_api_key_service(supabase)
            api_key_service.track_usage(key_data['id'], '/v1/generate', 500)
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


# ============================================================================
# Sessions API — Dashboard: list & resume past PDFs
# ============================================================================

@api_router.get("/sessions")
async def list_sessions(current_user: dict = Depends(get_current_user)):
    """Return the 30 most recent sessions for the authenticated user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        supabase = get_supabase_admin()
        result = (
            supabase.table("sessions")
            .select("session_id, title, mode, created_at")
            .eq("user_id", current_user["user_id"])
            .order("created_at", desc=True)
            .limit(30)
            .execute()
        )
        return {"sessions": result.data or []}
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/sessions/{session_id}")
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Return full session data (messages, latex, mode) for resuming in the editor."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        supabase = get_supabase_admin()
        result = (
            supabase.table("sessions")
            .select("session_id, title, mode, messages, current_latex, created_at")
            .eq("session_id", session_id)
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Session not found")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a session owned by the authenticated user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        supabase = get_supabase_admin()
        supabase.table("sessions").delete().eq("session_id", session_id).eq("user_id", current_user["user_id"]).execute()
        return {"success": True}
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PPT Generation (Legacy/Server kept)
# ============================================================================
@api_router.post("/generate-ppt", response_model=GeneratePPTResponse)
async def generate_ppt(request: GeneratePPTRequest, current_user: dict = Depends(get_current_user)):
    try:
        if not current_user: raise HTTPException(status_code=401, detail="Auth required")
        
        # FIX: current_user IS the user_data from deps.py. No need to query again.
        result = await ppt_generator_service.generate_presentation(
            request.topic, 
            request.content, 
            request.num_slides, 
            request.style, 
            current_user.get('name', 'User') # Use current_user directly
        )
        
        return GeneratePPTResponse(
            latex_content=result['latex_content'],
            slide_count=result['slide_count'],
            images_used=result.get('images_used', []),
            message=result['message'],
            session_id=str(uuid.uuid4())
        )
    except Exception as e:
        logger.error(f"PPT Generation Failed: {e}", exc_info=True)
        # Check if it was an auth error propagated
        if "401" in str(e):
             raise HTTPException(status_code=401, detail="Authentication failed during service call")
        raise HTTPException(status_code=500, detail=f"PPT Generation Failed: {str(e)}")

# Status
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    s = StatusCheck(**input.model_dump())
    get_supabase_client().table("status_checks").insert(s.model_dump(mode='json')).execute()
    return s

@api_router.get("/status")
async def get_status_checks():
    return get_supabase_client().table("status_checks").select("*").limit(50).execute().data

# Payment (Keep logic essentially mostly intact or delegate)
@api_router.post("/payment/create-checkout")
async def create_checkout(purchase: PurchaseRequest, current_user: dict = Depends(get_current_user)):
    if not current_user: raise HTTPException(status_code=401)
    return await payment_service.create_checkout_session(current_user['user_id'], purchase.plan, current_user['email'])

@api_router.post("/payment/success")
async def payment_success(plan: str, user_id: str, session_id: Optional[str] = None, payment_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    logger.info(f"Processing payment success for user={user_id} plan={plan} session={session_id} payment={payment_id}")

    # Security: if user is authenticated, make sure the user_id matches
    if current_user and current_user['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="User mismatch")

    # Map plan to credits added
    PLAN_CREDITS = {
        'credit_topup': 500,
        'pro': 100,
        'starter': 50,
    }
    credits_to_add = PLAN_CREDITS.get(plan, 100)  # Default 100 for unknown plans

    # For subscription plans (pro/starter), lock the plan name; for credit_topup keep existing plan
    is_subscription = plan in ('pro', 'starter')

    admin = get_supabase_admin()
    if not admin:
        logger.error("Supabase admin client not available")
        raise HTTPException(status_code=500, detail="Database unavailable")

    # Fetch user
    user_resp = admin.table("users").select("credits, plan").eq("user_id", user_id).execute()
    if not user_resp.data:
        logger.error(f"User {user_id} not found in database")
        raise HTTPException(status_code=404, detail="User not found")

    current_credits = user_resp.data[0].get('credits', 0)
    current_plan = user_resp.data[0].get('plan', 'free')

    new_total_credits = current_credits + credits_to_add
    final_plan = plan if is_subscription else current_plan

    admin.table("users").update({
        "credits": new_total_credits,
        "plan": final_plan,
    }).eq("user_id", user_id).execute()

    logger.info(f"Updated user {user_id}: credits {current_credits} -> {new_total_credits}, plan={final_plan}")

    return {
        "success": True,
        "message": "Payment processed successfully",
        "credits_added": credits_to_add,
        "plan": final_plan,
    }


app.include_router(api_router)
