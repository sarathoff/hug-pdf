from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict
from datetime import datetime
import uuid

class GenerateInitialRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    mode: Optional[str] = 'normal'

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
    current_latex: Optional[str] = None  # For PPT mode modifications
    mode: Optional[str] = 'normal'

class ChatResponse(BaseModel):
    html_content: str
    latex_content: Optional[str] = None
    message: str

class ConvertToPDFRequest(BaseModel):
    url: str
    conversion_type: str = 'article'
    options: Optional[dict] = {}

class ConvertToPDFResponse(BaseModel):
    latex_content: str
    message: str
    metadata: Optional[dict] = None
    conversion_type: str

class GeneratePPTRequest(BaseModel):
    topic: Optional[str] = None
    content: Optional[str] = None
    num_slides: int = 10
    style: str = "minimal"

class GeneratePPTResponse(BaseModel):
    latex_content: str
    slide_count: int
    images_used: List[Optional[str]] = []
    message: str
    session_id: Optional[str] = None

class OptimizeResumeResponse(BaseModel):
    latex_content: str
    ats_score: int
    improvements: List[str]
    message: str

class DownloadPDFRequest(BaseModel):
    latex_content: Optional[str] = None
    html_content: Optional[str] = None  # Fallback
    filename: Optional[str] = "document.pdf"
