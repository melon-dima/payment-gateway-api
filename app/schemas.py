from pydantic import BaseModel, EmailStr
from typing import Optional

# --- Auth ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# --- User ---
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    is_admin: bool = False

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_admin: Optional[bool] = None

# --- Account ---
class AccountResponse(BaseModel):
    id: int
    balance: float

# --- Payment ---
class PaymentResponse(BaseModel):
    id: int
    transaction_id: str
    amount: float
    created_at: str

# --- Webhook ---
class WebhookRequest(BaseModel):
    transaction_id: str
    account_id: int
    user_id: int
    amount: float
    signature: str