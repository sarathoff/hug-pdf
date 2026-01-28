from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends, UploadFile, File
from fastapi.responses import Response, FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
import logging
import requests

# Configure logging at startup
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

# Import services
from services.gemini_service import GeminiService
from services.pdf_service import PDFService
from services.auth_service import AuthService
from services.payment_service import PaymentService
from services.pexels_service import PexelsService
from services.rephrasy_service import RephrasyService
from services.content_converter_service import ContentConverterService
from services.pdf_extractor_service import PDFExtractorService
from services.resume_optimizer_service import ResumeOptimizerService
from services.ppt_generator_service import PPTGeneratorService
from models.session import Session, Message
from models.user import User, UserCreate, UserLogin, UserResponse
from dodopayments import DodoPayments

ROOT_DIR = Path(__file__).parent
# Load .env from project root (d:\pdf\.env) instead of backend folder
load_dotenv(ROOT_DIR.parent / '.env')

# Initialize Dodo Client
try:
    dodo_client = DodoPayments(
        bearer_token=os.environ.get('DODO_PAYMENTS_API_KEY')
    )
except Exception as e:
    logging.warning(f"Failed to initialize Dodo Client: {e}")
    dodo_client = None

# Supabase connection
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

try:
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase keys missing")
    supabase: Client = create_client(supabase_url, supabase_key)

    # Initialize Admin Client (Service Role) for bypassing RLS
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if service_role_key:
        supabase_admin: Client = create_client(supabase_url, service_role_key)
        logging.info("Supabase Admin client initialized with SERVICE_ROLE_KEY")
    else:
        logging.warning("SUPABASE_SERVICE_ROLE_KEY not found! Falling back to SUPABASE_KEY. RLS bypass will NOT work.")
        # Fallback (will likely fail for admin tasks)
        supabase_admin: Client = create_client(supabase_url, supabase_key)

except Exception as e:
    logging.warning(f"Failed to initialize Supabase Client: {e}")
    supabase = None
    supabase_admin = None

# Initialize services
gemini_service = GeminiService()
pdf_service = PDFService()
auth_service = AuthService()
payment_service = PaymentService()
pexels_service = PexelsService()
rephrasy_service = RephrasyService()
content_converter_service = ContentConverterService()
pdf_extractor_service = PDFExtractorService()
resume_optimizer_service = ResumeOptimizerService()
ppt_generator_service = PPTGeneratorService(gemini_service, pexels_service)


# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Dependency to get current user from token
async def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Get current user from JWT token using Supabase for persistence"""
    if not authorization or not authorization.startswith('Bearer '):
        return None

    token = authorization.replace('Bearer ', '')
    payload = auth_service.verify_token(token)
    if not payload:
        logging.warning("DEBUG: verify_token returned None")
        return None

    logging.info(f"DEBUG: Token verified. Payload: {payload}")

    if not supabase:
        logging.error("DEBUG: Supabase client is None")
        return None

    response = supabase.table("users").select("*").eq("user_id", payload['user_id']).execute()

    if not response.data:
        logging.warning(f"DEBUG: Authenticated user {payload['user_id']} not found in 'users' table. Auto-creating...")
        # Auto-create user if missing (Self-healing)
        try:
            if not supabase_admin:
                logging.error("Supabase Admin client not initialized, cannot auto-create user")
                return None

            new_user = {
                "user_id": payload['user_id'],
                "email": payload.get('email'),
                "credits": 3,
                "plan": "free"
            }
            # Use supabase_admin to bypass RLS
            res = supabase_admin.table("users").insert(new_user).execute()
            if res.data:
                logging.info(f"Auto-created user {payload['user_id']}")
                return res.data[0]
        except Exception as e:
            # Check if it's a duplicate key error (user was created by another request)
            error_str = str(e)
            if '23505' in error_str or 'duplicate key' in error_str.lower():
                logging.info(f"User {payload['user_id']} already exists (race condition), fetching existing record...")
                # Retry the SELECT to get the existing user (use admin client to bypass RLS)
                retry_response = supabase_admin.table("users").select("*").eq("user_id", payload['user_id']).execute()
                if retry_response.data:
                    return retry_response.data[0]

            logging.error(f"Failed to auto-create user: {e}")
            return None
        return None

    return response.data[0]

# Define Request/Response Models
class GenerateInitialRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    mode: Optional[str] = 'normal'  # 'normal', 'research', 'ebook'

class GenerateInitialResponse(BaseModel):
    session_id: str
    html_content: str
    latex_content: Optional[str] = None
    message: str
    credits_remaining: Optional[int] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str
    current_html: str
    mode: Optional[str] = 'normal'  # 'normal', 'research', 'ebook'

class ChatResponse(BaseModel):
    html_content: str
    latex_content: Optional[str] = None
    message: str

class DownloadPDFRequest(BaseModel):
    latex_content: Optional[str] = None
    html_content: Optional[str] = None  # Fallback
    filename: Optional[str] = "document.pdf"

class PurchaseRequest(BaseModel):
    plan: str  # 'founders' or 'pro'

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class RephrasyDetectRequest(BaseModel):
    text: str
    mode: Optional[str] = ""

class RephrasyDetectResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None

class RephrasyHumanizeRequest(BaseModel):
    text: str
    model: Optional[str] = "undetectable"
    language: Optional[str] = None
    words_based_pricing: Optional[bool] = True
    return_costs: Optional[bool] = True

class RephrasyHumanizeResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    flesch_score: Optional[float] = None
    costs: Optional[dict] = None
    error: Optional[str] = None

class ConvertToPDFRequest(BaseModel):
    url: str
    conversion_type: str = 'article'  # blog, article, website, resume, docs
    options: Optional[dict] = {}

class ConvertToPDFResponse(BaseModel):
    latex_content: str
    message: str
    metadata: Optional[dict] = None
    conversion_type: str

class OptimizeResumeResponse(BaseModel):
    latex_content: str
    ats_score: int
    improvements: List[str]
    message: str

class GeneratePPTRequest(BaseModel):
    topic: Optional[str] = None
    content: Optional[str] = None
    num_slides: int = 10
    style: str = "minimal"  # minimal, default, elegant

class GeneratePPTResponse(BaseModel):
    latex_content: str
    slide_count: int
    images_used: List[Optional[str]] = []
    message: str
    session_id: Optional[str] = None


# Routes
@api_router.get("/")
async def root():
    return {"message": "HugPDF API - Ready"}

@api_router.get("/auth/me")
async def get_me(current_user: Optional[dict] = Depends(get_current_user)):
    """Get current user data (bypasses RLS issues)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Fetch fresh data from DB using admin client
    try:
        if supabase_admin:
            logger.info(f"Fetching user data for user_id: {current_user['user_id']}")
            response = supabase_admin.table("users").select("*").eq("user_id", current_user['user_id']).execute()
            if response.data:
                logger.info(f"Returning user data: {response.data[0]}")
                return response.data[0]
        logger.warning("Supabase admin client not available, returning token data")
        return current_user  # Fallback to token data
    except Exception as e:
        logging.error(f"Failed to fetch user data: {e}")
        return current_user  # Fallback


@api_router.post("/generate-initial", response_model=GenerateInitialResponse)
async def generate_initial(
    request: GenerateInitialRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Generate initial HTML content from user prompt"""
    try:
        # Validate mode access for Pro-only features
        if request.mode in ['research', 'ebook']:
            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required for research and e-book modes"
                )
            # Allow Pro users and On-Demand users (who bought top-ups)
            if current_user.get('plan') not in ['pro', 'on_demand']:
                raise HTTPException(
                    status_code=402,
                    detail=f"{request.mode.capitalize()} mode is only available for Pro or On-Demand users. Please upgrade or top-up to access this feature."
                )

        # Note: Credits are now deducted on PDF download, not on generation
        remaining_credits = current_user['credits'] if current_user else None

        # Generate HTML using Gemini with mode support
        result = gemini_service.generate_html_from_prompt(request.prompt, mode=request.mode)

        # Create or get session
        session_id = request.session_id or str(uuid.uuid4())

        # Create session document
        session = Session(
            session_id=session_id,
            messages=[
                Message(role="user", content=request.prompt),
                Message(role="assistant", content=result["message"])
            ],
            current_html=result["html"],
            current_latex=result.get("latex")
        )

        # Store in Supabase
        if not supabase:
             logging.warning("Supabase client not initialized, skipping DB storage")
        else:
            data = session.model_dump(mode='json')
            supabase.table("sessions").upsert(data).execute()

        return GenerateInitialResponse(
            session_id=session_id,
            html_content=result["html"],
            latex_content=result.get("latex"),
            message=result["message"],
            credits_remaining=remaining_credits
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in generate_initial: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Handle chat messages to modify HTML"""
    try:
        # Validate mode access for Pro-only features
        if request.mode in ['research', 'ebook']:
            if not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required for research and e-book modes"
                )
            # Allow Pro users and On-Demand users (who bought top-ups)
            if current_user.get('plan') not in ['pro', 'on_demand']:
                raise HTTPException(
                    status_code=402,
                    detail=f"{request.mode.capitalize()} mode is only available for Pro or On-Demand users. Please upgrade or top-up to access this feature."
                )

        # Get session from Supabase
        response = supabase.table("sessions").select("*").eq("session_id", request.session_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Session not found")

        session_data = response.data[0]

        # Modify HTML and LaTeX using Gemini with mode support
        result = gemini_service.modify_html(
            request.current_html,
            request.message,
            current_latex=session_data.get('current_latex'),
            mode=request.mode
        )

        session = Session(**session_data)
        session.messages.append(Message(role="user", content=request.message))
        session.messages.append(Message(role="assistant", content=result["message"]))
        session.current_html = result["html"]
        if "latex" in result:
            session.current_latex = result["latex"]

        # Store updated session
        updated_data = session.model_dump(mode='json')
        supabase.table("sessions").update(updated_data).eq("session_id", request.session_id).execute()

        return ChatResponse(
            html_content=result["html"],
            latex_content=result.get("latex"),
            message=result["message"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class ModifyLatexRequest(BaseModel):
    session_id: Optional[str] = None
    modification: str
    current_latex: str
    mode: Optional[str] = 'normal'

class ModifyLatexResponse(BaseModel):
    latex_content: str
    html_content: str # For frontend compatibility, same as latex
    message: str

@api_router.post("/modify-latex", response_model=ModifyLatexResponse)
async def modify_latex(
    request: ModifyLatexRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Directly modify LaTeX content (used for image insertion etc)"""
    try:
        # Validate mode access if needed (similar to chat)
        if request.mode in ['research', 'ebook'] and not current_user:
             raise HTTPException(status_code=401, detail="Authentication required")

        result_latex = gemini_service.modify_latex(
            request.current_latex,
            request.modification,
            mode=request.mode
        )

        # Update session if session_id is provided
        if request.session_id:
             try:
                # Update DB via Supabase
                if supabase:
                    supabase.table("sessions").update({
                        "current_latex": result_latex,
                        "current_html": result_latex # Keep in sync
                    }).eq("session_id", request.session_id).execute()
             except Exception as e:
                 logging.warning(f"Failed to update session {request.session_id} in DB: {e}")

        return ModifyLatexResponse(
            latex_content=result_latex,
            html_content=result_latex,
            message="Content updated successfully"
        )
    except Exception as e:
        logging.error(f"Error in modify-latex: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/preview-pdf")
async def preview_pdf(request: DownloadPDFRequest):
    """Generate PDF preview from LaTeX content (no authentication required, fast single-pass)"""
    try:
        # Use LaTeX if available, otherwise fall back to HTML
        if request.latex_content:
            pdf_bytes = await pdf_service.generate_pdf(request.latex_content, preview_mode=True)
        elif request.html_content:
            # Treat html_content as LaTeX for backward compatibility
            pdf_bytes = await pdf_service.generate_pdf(request.html_content, preview_mode=True)
        else:
            raise HTTPException(status_code=400, detail="No content provided for PDF generation")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Type": "application/pdf",
                "Cache-Control": "no-cache"
            }
        )
    except Exception as e:
        logging.error(f"Error in preview_pdf: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/download-pdf")
async def download_pdf(
    request: DownloadPDFRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Convert LaTeX to PDF and return as download"""
    try:
        # Check if user has credits (authenticated users only)
        if current_user:
            if current_user['credits'] <= 0:
                raise HTTPException(
                    status_code=402,
                    detail="Insufficient PDFs remaining. Please purchase more to continue downloading."
                )

            # Deduct 1 credit (1 PDF) in Supabase
            if supabase_admin:
                supabase_admin.table("users").update({
                    'credits': current_user['credits'] - 1,
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }).eq('user_id', current_user['user_id']).execute()

                logger.info(f"Deducted 1 PDF credit from user {current_user['user_id']}. Remaining: {current_user['credits'] - 1}")

        # Use LaTeX if available, otherwise fall back to HTML (though HTML won't work well)
        if request.latex_content:
            pdf_bytes = await pdf_service.generate_pdf(request.latex_content)
        elif request.html_content:
            # For backward compatibility, but this won't work well
            raise HTTPException(
                status_code=400,
                detail="LaTeX content required for PDF generation. Please regenerate your document."
            )
        else:
            raise HTTPException(status_code=400, detail="No content provided for PDF generation")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename}",
                "Content-Type": "application/pdf"
            }
        )
    except Exception as e:
        logging.error(f"Error in download_pdf: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Authentication Routes (Using Supabase Auth)
@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return UserResponse(
        user_id=current_user['user_id'],
        email=current_user['email'],
        credits=current_user['credits'],
        plan=current_user['plan'],
        early_adopter=current_user.get('early_adopter', False)
    )

# Payment Routes
@api_router.post("/payment/create-checkout")
async def create_checkout(
    purchase: PurchaseRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create payment checkout session"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        result = await payment_service.create_checkout_session(
            current_user['user_id'],
            purchase.plan,
            current_user['email']
        )
        return result
    except Exception as e:
        logging.error(f"Error creating checkout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/payment/success")
async def payment_success(
    plan: str,
    user_id: str,
    session_id: Optional[str] = None,
    payment_id: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Handle successful payment - Verifies payment session and updates user credits"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not initialized")

    # CASE 1: Authenticated User
    if current_user:
        # Verify the user_id matches the authenticated user
        if current_user['user_id'] != user_id:
            logger.warning(f"User {current_user['user_id']} attempted to add credits to user {user_id}")
            raise HTTPException(status_code=403, detail="Cannot modify another user's credits")

    # CASE 2: Unauthenticated User (Session verification required)
    elif not session_id and not payment_id:
        # If not logged in AND no session/payment ID, we can't do anything
        raise HTTPException(status_code=401, detail="Authentication required or valid session/payment ID missing")

    # SECURITY: Verify payment with Dodo Payments if session_id or payment_id is provided
    # This is critical for unauthenticated requests and highly recommended for authenticated ones

    # Clean up session_id - if it's the literal placeholder string, treat it as None
    if session_id and (session_id == '{CHECKOUT_SESSION_ID}' or session_id == '%7BCHECKOUT_SESSION_ID%7D'):
        logger.warning(f"Received literal placeholder as session_id: {session_id}, treating as None")
        session_id = None

    verification_id = session_id or payment_id
    if verification_id:
        # Allow test sessions for local development
        if verification_id.startswith('test_session_'):
            logger.warning(f"TEST SESSION: Bypassing Dodo verification for {verification_id}")
            # For test sessions, we MUST trust the input user_id if unauthenticated
            # In production, test sessions should be disabled or strictly controlled
        else:
            # Real session - verify with Dodo Payments
            try:
                # Verify the payment session with Dodo Payments API
                dodo_api_key = os.environ.get('DODO_PAYMENTS_API_KEY')
                if not dodo_api_key:
                    logger.error("DODO_PAYMENTS_API_KEY not configured")
                    raise HTTPException(status_code=503, detail="Payment service not configured")

                headers = {
                    'Authorization': f'Bearer {dodo_api_key}',
                    'Content-Type': 'application/json'
                }

                # Get checkout session/payment details from Dodo
                # Try checkouts endpoint first (for sessions), then payments endpoint (for one-time payments)
                response = requests.get(
                    f'https://live.dodopayments.com/checkouts/{verification_id}',
                    headers=headers,
                    timeout=10
                )

                # If checkout not found, try payments endpoint
                if response.status_code == 404 and payment_id:
                    response = requests.get(
                        f'https://live.dodopayments.com/payments/{payment_id}',
                        headers=headers,
                        timeout=10
                    )

                if response.status_code != 200:
                    logger.error(f"Failed to verify payment {verification_id}: {response.status_code}")
                    raise HTTPException(status_code=400, detail="Payment verification failed")

                session_data = response.json()

                # Log the full session data for debugging
                logger.info(f"Dodo payment data for {verification_id}: {session_data}")

                # Verify the session is completed/paid
                session_status = session_data.get('status')
                # Removed 'free' from valid statuses - users must actually pay
                valid_statuses = ['completed', 'paid', 'succeeded']

                if session_status not in valid_statuses:
                    logger.warning(f"Payment {verification_id} has invalid status: {session_status}")
                    raise HTTPException(status_code=400, detail=f"Payment not completed. Status: {session_status}")

                # CRITICAL SECURITY: Verify actual payment was made (amount > 0)
                # EXCEPTION: Allow $0 payments if a valid coupon was applied (100% discount)
                total_amount = session_data.get('total_amount', 0)
                settlement_amount = session_data.get('settlement_amount', 0)

                # Check if a coupon/discount was applied
                discount_amount = session_data.get('discount_amount', 0)
                coupon_code = session_data.get('coupon_code')
                # Dodo may store coupons in different fields
                applied_coupons = session_data.get('coupons', [])
                has_coupon = bool(coupon_code or applied_coupons or discount_amount > 0)

                # For credit_topup, expect $2 (200 cents), for pro expect $5 (500 cents)
                expected_amounts = {
                    'credit_topup': 200,  # $2 in cents
                    'pro': 500  # $5 in cents
                }

                # Check if this is a test payment (total_amount = 0 is only allowed in test mode)
                payment_test_mode = os.environ.get('PAYMENT_TEST_MODE', 'false').lower() == 'true'

                if not payment_test_mode:
                    # Production mode - verify actual payment OR valid coupon
                    if total_amount <= 0 and settlement_amount <= 0:
                        # $0 payment detected - check if it's legitimate (coupon applied)
                        if has_coupon:
                            logger.info(f"✅ Accepting $0 payment for {plan} - Valid coupon applied. User: {user_id}, Coupon: {coupon_code or 'discount applied'}, Discount: ${discount_amount/100:.2f}")
                            # Allow the payment to proceed - it's a legitimate 100% discount
                        else:
                            # No coupon detected - this is suspicious
                            logger.error(f"Security Alert: Attempted to process $0 payment WITHOUT coupon for {plan}. User: {user_id}")
                            raise HTTPException(
                                status_code=400,
                                detail="Invalid payment: No payment amount detected and no coupon applied. Please contact support."
                            )
                    else:
                        # Non-zero payment - verify the amount matches expected (with tolerance for coupons/discounts)
                        expected_amount = expected_amounts.get(plan, 0)
                        actual_amount = max(total_amount, settlement_amount)

                        # If there's a discount, the actual amount may be less than expected
                        # Only verify minimum amount if NO discount was applied
                        if not has_coupon:
                            # Allow 10% tolerance for currency conversion/fees
                            min_expected = expected_amount * 0.9

                            if actual_amount < min_expected:
                                logger.error(f"Security Alert: Payment amount mismatch. Expected: {expected_amount}, Got: {actual_amount}")
                                raise HTTPException(
                                    status_code=400,
                                    detail=f"Payment amount verification failed. Expected at least ${expected_amount/100:.2f}, received ${actual_amount/100:.2f}"
                                )
                        else:
                            logger.info(f"Payment with discount accepted: ${actual_amount/100:.2f} (Original: ${expected_amount/100:.2f}, Discount: ${discount_amount/100:.2f})")
                else:
                    # Test mode - allow $0 payments but log it
                    logger.warning(f"TEST MODE: Processing $0 payment for {plan}. User: {user_id}")

                # Verify user_id matches the one in metadata (TRUSTED SOURCE)
                metadata = session_data.get('metadata', {})
                metadata_user_id = metadata.get('user_id')
                metadata_plan = metadata.get('plan')

                if not metadata_user_id or metadata_user_id != user_id:
                    logger.error(f"Security Mismatch: Request user_id {user_id} != Metadata user_id {metadata_user_id}")
                    raise HTTPException(status_code=400, detail="Payment verification failed: User ID mismatch")

                if metadata_plan != plan:
                    logger.warning(f"Plan mismatch: Request {plan} != Metadata {metadata_plan}, using metadata plan")
                    plan = metadata_plan

                logger.info(f"Payment verified for user {user_id} via Dodo {verification_id}")

            except requests.RequestException as e:
                logger.error(f"Error verifying payment with Dodo: {str(e)}")
                raise HTTPException(status_code=503, detail="Payment verification service unavailable")
    else:
        # No session_id or payment_id provided
        if current_user:
            # TEMPORARY: Allow authenticated users to proceed without verification
            # This is needed because Dodo Payments subscriptions don't provide session_id/payment_id in return URL
            # TODO: Implement webhook-based verification for proper security
            logger.warning(f"SECURITY WARNING: Processing payment for authenticated user {user_id} without Dodo verification")
            logger.warning(f"Plan: {plan}. This should be verified via webhook in production.")
            # Continue to process payment - user is authenticated
        else:
            # Unauthenticated users absolutely require verification
            logger.error(f"Security Alert: Unauthenticated payment attempt without verification ID")
            raise HTTPException(
                status_code=401,
                detail="Authentication and payment verification required"
            )

    try:
        # Check if this payment has already been processed (idempotency check)
        if verification_id:
            try:
                # Check if we've already processed this session/payment
                existing = supabase_admin.table("payment_sessions").select("*").eq("session_id", verification_id).execute()
                if existing.data:
                    logger.warning(f"Payment {verification_id} already processed, skipping credit addition")
                    return {
                        'success': True,
                        'message': 'Payment already processed',
                        'credits_added': 0,
                        'plan': plan
                    }
            except Exception as e:
                # Table might not exist - log and continue
                logger.info(f"Could not check payment_sessions table (may not exist): {e}")

        # Update credits based on plan
        if plan == 'credit_topup':
            credits_to_add = 20
        else:
            credits_to_add = 50  # Pro: 50 PDFs/month

        # Get current user details to determine plan update strategy
        # Use admin client to bypass RLS
        resp = supabase_admin.table("users").select("credits, plan").eq("user_id", user_id).execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="User not found")

        current_db_user = resp.data[0]
        new_credits = current_db_user['credits'] + credits_to_add
        current_plan = current_db_user['plan']

        # Determine new plan
        # If buying Pro, set to Pro.
        # If buying Top-up:
        #   - If currently Free -> Upgrade to 'on_demand' (unlocks features)
        #   - If currently Pro -> Stay Pro
        #   - If currently On_Demand -> Stay On_Demand
        if plan == 'credit_topup':
            if current_plan == 'pro':
                final_plan = 'pro'
            else:
                final_plan = 'on_demand'
        else:
            final_plan = plan  # e.g., 'pro'

        logger.info(f"Updating user {user_id}: old_plan={current_plan}, new_plan={final_plan}, new_credits={new_credits}")

        # Update user plan and credits using admin client to bypass RLS
        update_response = supabase_admin.table("users").update({
            'plan': final_plan,
            'credits': new_credits,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).eq('user_id', user_id).execute()

        # Verify the update was successful
        if not update_response.data:
            logger.error(f"Failed to update user {user_id} - no data returned from update")
            raise HTTPException(status_code=500, detail="Failed to update user plan and credits")

        logger.info(f"User {user_id} updated successfully: {update_response.data}")

        # Record this payment session to prevent duplicates (optional)
        if verification_id:
            try:
                supabase_admin.table("payment_sessions").insert({
                    'session_id': verification_id,
                    'user_id': user_id,
                    'plan': plan,
                    'credits_added': credits_to_add,
                    'processed_at': datetime.now(timezone.utc).isoformat()
                }).execute()
            except Exception as e:
                logger.info(f"Could not record payment session (table may not exist): {e}")

        logger.info(f"Added {credits_to_add} credits to user {user_id} for plan {plan}")

        return {
            'success': True,
            'credits_added': credits_to_add,
            'plan': plan,
            'new_total_credits': new_credits,
            'message': f'Successfully upgraded to {plan} plan with {credits_to_add} credits added'
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in payment success: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/pricing")
async def get_pricing():
    """Get pricing plans"""
    return {
        'plans': [
            {
                'id': 'credit_topup',
                'name': 'Credit Top-Up',
                'price': 2,
                'billing': 'one-time',
                'credits': 20,
                'popular': True,
                'features': ['20 Credits added instantly', 'Unlocks Research & E-book modes', 'Removes Watermarks', 'Never expires', 'One-time payment']
            }
        ]
    }

@api_router.get("/images/search")
async def search_images(query: str, per_page: int = 15, page: int = 1):
    """Search for images on Pexels"""
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")

        result = pexels_service.search_images(query, per_page, page)

        if result is None:
            raise HTTPException(status_code=503, detail="Image search service unavailable")

        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error searching images: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/images/curated")
async def get_curated_images(per_page: int = 15, page: int = 1):
    """Get curated images from Pexels"""
    try:
        result = pexels_service.get_curated_images(per_page, page)

        if result is None:
            raise HTTPException(status_code=503, detail="Image service unavailable")

        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting curated images: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Upload image and return temporary URL for use in PDFs"""
    try:
        # Create temp_uploads directory if it doesn't exist
        temp_dir = ROOT_DIR / "temp_uploads"
        temp_dir.mkdir(exist_ok=True)

        # Generate unique filename
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_name = f"{uuid.uuid4()}.{file_ext}"
        filepath = temp_dir / unique_name

        # Save file
        content = await file.read()
        with open(filepath, 'wb') as f:
            f.write(content)

        # Get backend URL from environment or construct it
        backend_url = os.environ.get('BACKEND_URL', 'http://localhost:8000')
        url = f"{backend_url}/api/temp-images/{unique_name}"

        logger.info(f"Uploaded image {file.filename} as {unique_name}")
        return {"url": url, "filename": file.filename}

    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/temp-images/{filename}")
async def serve_temp_image(filename: str):
    """Serve temporarily uploaded images"""
    temp_dir = (ROOT_DIR / "temp_uploads").resolve()
    filepath = (temp_dir / filename).resolve()

    # Security check: Prevent path traversal
    if not filepath.is_relative_to(temp_dir):
        logger.warning(f"Path traversal attempt: {filename}")
        raise HTTPException(status_code=404, detail="Image not found")

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(filepath)


@api_router.post("/convert-to-pdf", response_model=ConvertToPDFResponse)
async def convert_to_pdf(
    request: ConvertToPDFRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Convert any web content to professional PDF"""
    try:
        # Validate URL
        if not content_converter_service.validate_url(request.url):
            raise HTTPException(
                status_code=400,
                detail="Invalid URL. Please provide a valid web URL (e.g., https://example.com/blog-post)"
            )

        # Validate conversion type
        valid_types = ['blog', 'article', 'website', 'resume', 'docs']
        if request.conversion_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid conversion type. Must be one of: {', '.join(valid_types)}"
            )

        # Convert content to PDF
        logger.info(f"Converting {request.conversion_type} from: {request.url}")
        result = content_converter_service.convert_to_pdf(
            url=request.url,
            conversion_type=request.conversion_type,
            options=request.options or {}
        )

        if not result:
            raise HTTPException(
                status_code=400,
                detail="Failed to convert content. Please ensure the URL is accessible and contains valid content."
            )

        return ConvertToPDFResponse(
            latex_content=result['latex'],
            message=result['message'],
            metadata=result.get('metadata', {}),
            conversion_type=result['conversion_type']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in convert_to_pdf: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/optimize-resume", response_model=OptimizeResumeResponse)
async def optimize_resume(
    resume_pdf: UploadFile = File(...),
    job_description: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Optimize resume PDF for ATS compatibility with optional job description"""
    try:
        # Validate file type
        if not resume_pdf.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload a PDF file."
            )

        # Read PDF file
        pdf_content = await resume_pdf.read()

        # Validate PDF
        if not pdf_extractor_service.validate_pdf(pdf_content):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file. Please upload a valid PDF resume."
            )

        # Extract text from PDF
        logger.info(f"Extracting text from PDF: {resume_pdf.filename}")
        resume_text = pdf_extractor_service.extract_text_from_pdf(pdf_content)

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract text from PDF. Please ensure the PDF contains readable text."
            )

        # Optimize resume
        logger.info(f"Optimizing resume{' for specific job' if job_description else ' (general ATS optimization)'}")
        result = resume_optimizer_service.optimize_resume(
            resume_text=resume_text,
            job_description=job_description
        )

        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to optimize resume. Please try again."
            )

        return OptimizeResumeResponse(
            latex_content=result['latex'],
            ats_score=result['ats_score'],
            improvements=result['improvements'],
            message=result['message']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in optimize_resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/rephrasy/detect", response_model=RephrasyDetectResponse)
async def detect_ai_content(
    request: RephrasyDetectRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Detect if content is AI-generated using Rephrasy API"""
    try:
        result = rephrasy_service.detect_ai_content(request.text, request.mode)

        if result is None:
            return RephrasyDetectResponse(
                success=False,
                error="Rephrasy detection service unavailable or API key not configured"
            )

        return RephrasyDetectResponse(
            success=True,
            result=result
        )
    except Exception as e:
        logger.error(f"Error in detect_ai_content: {str(e)}")
        return RephrasyDetectResponse(
            success=False,
            error=str(e)
        )

@api_router.post("/rephrasy/humanize", response_model=RephrasyHumanizeResponse)
async def humanize_content(
    request: RephrasyHumanizeRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Humanize AI-generated content using Rephrasy API"""
    try:
        result = rephrasy_service.humanize_content(
            text=request.text,
            model=request.model,
            language=request.language,
            words_based_pricing=request.words_based_pricing,
            return_costs=request.return_costs
        )

        if result is None:
            return RephrasyHumanizeResponse(
                success=False,
                error="Rephrasy humanization service unavailable or API key not configured"
            )

        return RephrasyHumanizeResponse(
            success=True,
            output=result.get('output'),
            flesch_score=result.get('new_flesch_score'),
            costs=result.get('costs')
        )
    except Exception as e:
        logger.error(f"Error in humanize_content: {str(e)}")
        return RephrasyHumanizeResponse(
            success=False,
            error=str(e)
        )

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump(mode='json')
    supabase.table("status_checks").insert(doc).execute()
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    response = supabase.table("status_checks").select("*").limit(100).order('timestamp', desc=True).execute()
    return response.data

@api_router.post("/generate-ppt", response_model=GeneratePPTResponse)
async def generate_ppt(
    request: GeneratePPTRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Generate a professional presentation from topic or content"""
    try:
        # Validate inputs
        if not request.topic and not request.content:
            raise HTTPException(
                status_code=400,
                detail="Either 'topic' or 'content' must be provided"
            )

        if request.num_slides < 5 or request.num_slides > 30:
            raise HTTPException(
                status_code=400,
                detail="Number of slides must be between 5 and 30"
            )

        if request.style not in ["minimal", "default", "elegant"]:
            raise HTTPException(
                status_code=400,
                detail="Style must be 'minimal', 'default', or 'elegant'"
            )

        # Check authentication
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        user_id = current_user.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user data")

        # Get user data
        if supabase_admin:
            user_response = supabase_admin.table("users").select("*").eq("user_id", user_id).execute()

            if not user_response.data:
                raise HTTPException(status_code=404, detail="User not found")

            user_data = user_response.data[0]
            user_plan = user_data.get('plan', 'free')
            ppt_count = user_data.get('ppt_count', 0)

            # Check if user has credits
            credits = user_data.get('credits', 0)

            if credits < 1:
                raise HTTPException(
                    status_code=402,
                    detail="You don't have enough credits to generate a presentation. Please upgrade your plan or purchase more credits."
                )

        # Generate presentation
        logger.info(f"Generating PPT for user {user_id}: topic={request.topic}, content_length={len(request.content) if request.content else 0}")

        result = await ppt_generator_service.generate_presentation(
            topic=request.topic,
            content=request.content,
            num_slides=request.num_slides,
            style=request.style,
            user_name=user_data.get('name', 'User')
        )

        # Deduct 1 credit
        if supabase_admin:
            new_credits = credits - 1
            supabase_admin.table("users").update({
                "credits": new_credits
            }).eq("user_id", user_id).execute()

            logger.info(f"Deducted 1 credit for PPT generation. User {user_id} now has {new_credits} credits.")

        # Create a new session for this PPT
        session_id = str(uuid.uuid4())

        if supabase:
            new_session = {
                "session_id": session_id,
                "user_id": user_id,
                "mode": "ppt",
                "title": request.topic if request.topic else "Presentation from content"
            }
            supabase.table("sessions").insert(new_session).execute()

            # Save the initial message
            initial_message = {
                "session_id": session_id,
                "role": "assistant",
                "content": result['message']
            }
            supabase.table("messages").insert(initial_message).execute()

        return GeneratePPTResponse(
            latex_content=result['latex_content'],
            slide_count=result['slide_count'],
            images_used=result['images_used'],
            message=result['message'],
            session_id=session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PPT: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate presentation: {str(e)}")

class CheckoutRequest(BaseModel):
    productId: str
    email: str

@api_router.post("/checkout")
async def create_checkout_session(request: CheckoutRequest):
    """Old checkout endpoint for backward compatibility"""
    if not dodo_client:
        raise HTTPException(status_code=503, detail="Payment service not initialized")
    try:
        session = dodo_client.checkout_sessions.create(
            product_cart=[{'product_id': request.productId, 'quantity': 1}],
            customer={'email': request.email},
            return_url=f"{os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')[0]}/success"
        )
        return {"url": session.checkout_url}
    except Exception as e:
        logging.error(f"Dodo Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Checkout failed")

# Add root endpoint to main app
@app.get("/")
async def root():
    return {"message": "HugPDF Backend API", "status": "running", "version": "1.0.1"}

# Include the router in the main app
app.include_router(api_router)

origins_str = os.environ.get('CORS_ORIGINS', '*')
if origins_str == '*':
    origins = ["*"]
else:
    origins = [o.strip() for o in origins_str.split(',') if o.strip()]

logging.info(f"Active CORS Origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)