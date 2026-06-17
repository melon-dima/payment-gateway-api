from sanic import Blueprint, json
from sqlalchemy import select

from app.db import async_session_maker
from app.models import User, Account
from app.auth import admin_required, get_password_hash
from app.schemas import UserCreate, UserUpdate

admin_bp = Blueprint("admin", url_prefix="/admin")

@admin_bp.get("/me")
@admin_required
async def get_admin_me(request):
    user = request.ctx.user
    return json({"id": user.id, "email": user.email, "full_name": user.full_name})

@admin_bp.get("/users")
@admin_required
async def get_users(request):
    async with async_session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        response = []
        for u in users:
            acc_result = await session.execute(select(Account).where(Account.user_id == u.id))
            accounts = acc_result.scalars().all()
            response.append({
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "accounts": [{"id": a.id, "balance": a.balance} for a in accounts]
            })
        return json(response)

@admin_bp.post("/users")
@admin_required
async def create_user(request):
    data = UserCreate(**request.json)
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            return json({"error": "Email already registered"}, 400)
            
        new_user = User(
            email=data.email,
            password_hash=get_password_hash(data.password),
            full_name=data.full_name,
            is_admin=data.is_admin
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return json({"id": new_user.id, "email": new_user.email, "full_name": new_user.full_name}, 201)

@admin_bp.put("/users/<user_id:int>")
@admin_required
async def update_user(request, user_id):
    data = UserUpdate(**request.json)
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return json({"error": "User not found"}, 404)
            
        if data.email: user.email = data.email
        if data.full_name: user.full_name = data.full_name
        if data.password: user.password_hash = get_password_hash(data.password)
        if data.is_admin is not None: user.is_admin = data.is_admin
        
        await session.commit()
        return json({"id": user.id, "email": user.email, "full_name": user.full_name})

@admin_bp.delete("/users/<user_id:int>")
@admin_required
async def delete_user(request, user_id):
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return json({"error": "User not found"}, 404)
            
        await session.delete(user)
        await session.commit()
        return json({"message": "User deleted"})