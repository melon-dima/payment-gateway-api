from datetime import datetime, timedelta
from functools import wraps
from jose import JWTError, jwt
from passlib.context import CryptContext
from sanic import json
from sqlalchemy import select

from app.config import get_settings
from app.db import async_session_maker
from app.models import User

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Декоратор для защиты роутов
def protected(f):
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return json({"error": "Missing or invalid token"}, 401)
        
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: int = payload.get("sub")
            if user_id is None:
                raise ValueError
        except (JWTError, ValueError):
            return json({"error": "Invalid token"}, 401)

        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                return json({"error": "User not found"}, 404)
            request.ctx.user = user
        
        return await f(request, *args, **kwargs)
    return decorated_function

# Декоратор для проверки прав администратора
def admin_required(f):
    @wraps(f)
    @protected
    async def decorated_function(request, *args, **kwargs):
        if not request.ctx.user.is_admin:
            return json({"error": "Admin privileges required"}, 403)
        return await f(request, *args, **kwargs)
    return decorated_function