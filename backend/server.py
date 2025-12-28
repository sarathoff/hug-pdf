from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends
from fastapi.responses import Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
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


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

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
    """Get current user from JWT token"""
    if not authorization or not authorization.startswith('Bearer '):
        return None
    
    token = authorization.replace('Bearer ', '')
    payload = auth_service.verify_token(token)
    if not payload:
        return None
    
    user = await db.users.find_one({'user_id': payload['user_id']})
    return user

# Define Request/Response Models
class GenerateInitialRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None

class GenerateInitialResponse(BaseModel):
    session_id: str
    html_content: str
    message: str
    credits_remaining: Optional[int] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str
    current_html: str

class ChatResponse(BaseModel):
    html_content: str
    message: str

class DownloadPDFRequest(BaseModel):
    html_content: str
    filename: Optional[str] = "document.pdf"

class PurchaseRequest(BaseModel):
    plan: str  # 'founders' or 'pro'

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "PDF Generator API - Ready"}

@api_router.post("/generate-initial", response_model=GenerateInitialResponse)
async def generate_initial(
    request: GenerateInitialRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Generate initial HTML content from user prompt"""
    try:
        # Check if user has credits (authenticated users only)
        if current_user:
            if current_user['credits'] <= 0:
                raise HTTPException(
                    status_code=402,
                    detail="Insufficient credits. Please purchase more credits to continue."
                )
            
            # Deduct 1 credit
            await db.users.update_one(
                {'user_id': current_user['user_id']},
                {
                    '$inc': {'credits': -1},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            remaining_credits = current_user['credits'] - 1
        else:
            # Allow guests to use with limitations (optional)
            remaining_credits = None
        
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
            current_html=result["html"]
        )
        
        # Store in MongoDB
        await db.sessions.update_one(
            {"session_id": session_id},
            {"$set": session.dict()},
            upsert=True
        )
        
        return GenerateInitialResponse(
            session_id=session_id,
            html_content=result["html"],
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
        # Get session from database
        session_doc = await db.sessions.find_one({"session_id": request.session_id})
        if not session_doc:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Modify HTML using Gemini
        result = gemini_service.modify_html(request.current_html, request.message)
        
        # Update session
        session = Session(**session_doc)
        session.messages.append(Message(role="user", content=request.message))
        session.messages.append(Message(role="assistant", content=result["message"]))
        session.current_html = result["html"]
        
        # Store updated session
        await db.sessions.update_one(
            {"session_id": request.session_id},
            {"$set": session.dict()}
        )
        
        return ChatResponse(
            html_content=result["html"],
            message=result["message"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/download-pdf")
async def download_pdf(request: DownloadPDFRequest):
    """Convert HTML to PDF and return as download"""
    try:
        # Generate PDF
        pdf_bytes = await pdf_service.generate_pdf(request.html_content)
        
        # Return as downloadable file
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

# Authentication Routes
@api_router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register new user with 3 free credits"""
    try:
        # Check if user exists
        existing_user = await db.users.find_one({'email': user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user = User(
            email=user_data.email,
            password_hash=auth_service.hash_password(user_data.password),
            credits=3,
            plan="free"
        )
        
        await db.users.insert_one(user.dict())
        
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            credits=user.credits,
            plan=user.plan,
            early_adopter=user.early_adopter
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in register: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    """Login and get JWT token"""
    try:
        user = await db.users.find_one({'email': credentials.email})
        if not user or not auth_service.verify_password(credentials.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        token = auth_service.create_token(user['user_id'], user['email'])
        
        return {
            'token': token,
            'user': UserResponse(
                user_id=user['user_id'],
                email=user['email'],
                credits=user['credits'],
                plan=user['plan'],
                early_adopter=user.get('early_adopter', False)
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
    user_id: str
):
    """Handle successful payment"""
    try:
        user = await db.users.find_one({'user_id': user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update credits based on plan
        credits_to_add = 150 if plan == 'founders' else 100
        early_adopter = plan == 'founders'
        
        await db.users.update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'plan': plan,
                    'early_adopter': early_adopter,
                    'updated_at': datetime.utcnow()
                },
                '$inc': {'credits': credits_to_add}
            }
        )
        
        return {'success': True, 'credits_added': credits_to_add}
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
                'id': 'free',
                'name': 'Free Starter',
                'price': 0,
                'billing': 'one-time',
                'credits': 3,
                'features': ['3 Credits', 'To try the "Aha!" moment']
            },
            {
                'id': 'founders',
                'name': 'Founder\'s Pack',
                'price': 19,
                'billing': 'one-time',
                'credits': 150,
                'features': ['150 Credits', 'Early Adopter badge', 'Best for quick cash']
            },
            {
                'id': 'pro',
                'name': 'Pro Monthly',
                'price': 9,
                'billing': 'monthly',
                'credits': 100,
                'features': ['100 Credits every month', 'Custom Templates']
            }
        ]
    }

        # Generate PDF
        pdf_bytes = await pdf_service.generate_pdf(request.html_content)
        
        # Return as downloadable file
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

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()