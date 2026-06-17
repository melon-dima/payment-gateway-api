from sanic import Blueprint, json
from sqlalchemy import select

from app.db import async_session_maker
from app.models import Account, Payment
from app.auth import protected

user_bp = Blueprint("user", url_prefix="/user")

@user_bp.get("/me")
@protected
async def get_me(request):
    user = request.ctx.user
    return json({"id": user.id, "email": user.email, "full_name": user.full_name})

@user_bp.get("/accounts")
@protected
async def get_accounts(request):
    user = request.ctx.user
    async with async_session_maker() as session:
        result = await session.execute(select(Account).where(Account.user_id == user.id))
        accounts = result.scalars().all()
        return json([{"id": a.id, "balance": a.balance} for a in accounts])

@user_bp.get("/payments")
@protected
async def get_payments(request):
    user = request.ctx.user
    async with async_session_maker() as session:
        result = await session.execute(select(Payment).where(Payment.user_id == user.id))
        payments = result.scalars().all()
        return json([{
            "id": p.id, 
            "transaction_id": p.transaction_id, 
            "amount": p.amount,
            "created_at": p.created_at.isoformat()
        } for p in payments])