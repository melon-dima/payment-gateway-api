from sanic import Blueprint, json
from sqlalchemy import select

from app.db import async_session_maker
from app.models import User
from app.schemas import LoginRequest
from app.auth import verify_password, create_access_token

auth_bp = Blueprint("auth", url_prefix="/auth")

@auth_bp.post("/login")
async def login(request):
    data = LoginRequest(**request.json)
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(data.password, user.password_hash):
            return json({"error": "Invalid credentials"}, 401)
            
        token = create_access_token({"sub": user.id, "is_admin": user.is_admin})
        return json({"access_token": token, "token_type": "bearer"})