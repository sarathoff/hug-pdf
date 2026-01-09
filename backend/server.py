from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends
from fastapi.responses import Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
import logging
import requests

# Configure logging at startup
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
    # Try to get explicit service role key, otherwise fallback to SUPABASE_KEY (hoping it IS the service role)
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", supabase_key)
    supabase_admin: Client = create_client(supabase_url, service_role_key)

except Exception as e:
    logging.warning(f"Failed to initialize Supabase Client: {e}")
    supabase = None
    supabase_admin = None

# Initialize services
gemini_service = GeminiService()
pdf_service = PDFService()
auth_service = AuthService()
payment_service = PaymentService()

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
            logging.error(f"Failed to auto-create user: {e}")
            return None
        return None

    return response.data[0]

# Define Request/Response Models
class GenerateInitialRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None

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

# Routes
@api_router.get("/")
async def root():
    return {"message": "HugPDF API - Ready"}

@api_router.post("/generate-initial", response_model=GenerateInitialResponse)
async def generate_initial(
    request: GenerateInitialRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Generate initial HTML content from user prompt"""
    try:
        # Note: Credits are now deducted on PDF download, not on generation
        remaining_credits = current_user['credits'] if current_user else None

        # Generate HTML using Gemini
        result = gemini_service.generate_html_from_prompt(request.prompt)

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
async def chat(request: ChatRequest):
    """Handle chat messages to modify HTML"""
    try:
        # Get session from Supabase
        response = supabase.table("sessions").select("*").eq("session_id", request.session_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Session not found")

        session_data = response.data[0]

        # Modify HTML and LaTeX using Gemini
        result = gemini_service.modify_html(
            request.current_html,
            request.message,
            current_latex=session_data.get('current_latex')
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

@api_router.post("/preview-pdf")
async def preview_pdf(request: DownloadPDFRequest):
    """Generate PDF preview from LaTeX content (no authentication required)"""
    try:
        # Use LaTeX if available, otherwise fall back to HTML
        if request.latex_content:
            pdf_bytes = await pdf_service.generate_pdf(request.latex_content)
        elif request.html_content:
            # Treat html_content as LaTeX for backward compatibility
            pdf_bytes = await pdf_service.generate_pdf(request.html_content)
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
            if supabase:
                supabase.table("users").update({
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
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Handle successful payment - REQUIRES AUTHENTICATION AND PAYMENT VERIFICATION"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not initialized")

    # SECURITY: Require authentication
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # SECURITY: Verify the user_id matches the authenticated user
    if current_user['user_id'] != user_id:
        logger.warning(f"User {current_user['user_id']} attempted to add credits to user {user_id}")
        raise HTTPException(status_code=403, detail="Cannot modify another user's credits")

    # SECURITY: Verify payment with Dodo Payments
    if not session_id:
        # No session_id provided - reject
        logger.warning(f"Payment success called without session_id for user {user_id}")
        raise HTTPException(status_code=400, detail="Payment session ID required")

    # Allow test sessions for local development ONLY if explicitly enabled
    payment_test_mode = os.environ.get('PAYMENT_TEST_MODE', 'false').lower() == 'true'

    if session_id.startswith('test_session_'):
        if not payment_test_mode:
            logger.warning(
                f"SECURITY ALERT: Attempted test session bypass in production: {session_id}"
            )
            raise HTTPException(
                status_code=403, detail="Test sessions not allowed in production"
            )

        logger.warning(f"TEST SESSION: Bypassing Dodo verification for {session_id}")
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

            # Get checkout session details from Dodo
            response = requests.get(
                f'https://live.dodopayments.com/checkouts/{session_id}',
                headers=headers,
                timeout=10
            )

            if response.status_code != 200:
                logger.error(f"Failed to verify payment session {session_id}: {response.status_code}")
                raise HTTPException(status_code=400, detail="Payment verification failed")

            session_data = response.json()

            # Verify the session is completed/paid
            session_status = session_data.get('status')
            if session_status != 'completed':
                logger.warning(f"Payment session {session_id} status is {session_status}, not completed")
                raise HTTPException(status_code=400, detail=f"Payment not completed. Status: {session_status}")

            # Verify the metadata matches
            metadata = session_data.get('metadata', {})
            if metadata.get('user_id') != user_id or metadata.get('plan') != plan:
                logger.error(f"Payment session metadata mismatch for {session_id}")
                raise HTTPException(status_code=400, detail="Payment verification failed: metadata mismatch")

            logger.info(f"Payment verified for user {user_id}, session {session_id}")

        except requests.RequestException as e:
            logger.error(f"Error verifying payment with Dodo: {str(e)}")
            raise HTTPException(status_code=503, detail="Payment verification service unavailable")

    try:
        # Check if this payment has already been processed (idempotency check)
        if session_id:
            try:
                # Check if we've already processed this session
                existing = supabase.table("payment_sessions").select("*").eq("session_id", session_id).execute()
                if existing.data:
                    logger.warning(f"Payment session {session_id} already processed, skipping credit addition")
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
        # Credits now represent PDF downloads: 1 credit = 1 PDF
        credits_to_add = 2000 if plan == 'lifetime' else 50  # Lifetime: 2000 PDFs, Pro: 50 PDFs/month
        is_lifetime = plan == 'lifetime'

        # Get current user for increment
        resp = supabase.table("users").select("credits").eq("user_id", user_id).execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="User not found")

        new_credits = resp.data[0]['credits'] + credits_to_add

        supabase_admin.table("users").update({
            'plan': plan,
            'credits': new_credits,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).eq('user_id', user_id).execute()

        # Record this payment session to prevent duplicates (optional)
        if session_id:
            try:
                supabase.table("payment_sessions").insert({
                    'session_id': session_id,
                    'user_id': user_id,
                    'plan': plan,
                    'credits_added': credits_to_add,
                    'processed_at': datetime.now(timezone.utc).isoformat()
                }).execute()
            except Exception as e:
                # Table might not exist - log but don't fail
                logger.info(f"Could not record payment session (table may not exist): {e}")

        logger.info(f"Added {credits_to_add} credits to user {user_id} for plan {plan}")
        return {'success': True, 'credits_added': credits_to_add, 'plan': plan}
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
                'id': 'pro',
                'name': 'Pro Monthly',
                'price': 9,
                'billing': 'monthly',
                'credits': 50,
                'features': ['50 PDF downloads every month', 'AI-powered PDF generation', 'Unlimited document editing', 'Priority support']
            },
            {
                'id': 'lifetime',
                'name': 'Lifetime Access',
                'price': 39,
                'billing': 'one-time',
                'credits': 2000,
                'popular': True,
                'features': ['2000 PDF downloads', 'Lifetime access', 'All future updates', 'Premium support', 'Early access to new features']
            }
        ]
    }

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
