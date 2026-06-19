from typing import Optional

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


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


class WebhookRequest(BaseModel):
    transaction_id: str
    account_id: int
    user_id: int
    amount: float
    signature: str
