from pydantic import BaseModel, Field
from typing import Optional

class StatusCheck(BaseModel):
    id: str
    client_name: str
    timestamp: str

class StatusCheckCreate(BaseModel):
    client_name: str

class PurchaseRequest(BaseModel):
    plan: str
