import hashlib
from sanic import Blueprint, json
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.db import async_session_maker
from app.models import Account, Payment, User
from app.schemas import WebhookRequest
from app.config import get_settings

webhook_bp = Blueprint("webhook", url_prefix="/webhook")
settings = get_settings()

@webhook_bp.post("/payment")
async def payment_webhook(request):
    try:
        data = WebhookRequest(**request.json)
    except Exception:
        return json({"error": "Invalid payload"}, 400)

    # 1. Проверка подписи
    # Формула: {account_id}{amount}{transaction_id}{user_id}{secret_key}
    raw_string = f"{data.account_id}{data.amount}{data.transaction_id}{data.user_id}{settings.WEBHOOK_SECRET_KEY}"
    expected_signature = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
    
    if data.signature != expected_signature:
        return json({"error": "Invalid signature"}, 403)

    async with async_session_maker() as session:
        # 2. Проверка уникальности транзакции (Идемпотентность)
        result = await session.execute(
            select(Payment).where(Payment.transaction_id == data.transaction_id)
        )
        if result.scalar_one_or_none():
            return json({"message": "Transaction already processed"}, 200)

        # 3. Проверка существования пользователя
        user_result = await session.execute(select(User).where(User.id == data.user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            return json({"error": "User not found"}, 404)

        # 4. Проверка/создание счета
        account_result = await session.execute(
            select(Account).where(Account.id == data.account_id, Account.user_id == data.user_id)
        )
        account = account_result.scalar_one_or_none()
        
        if not account:
            account = Account(id=data.account_id, user_id=data.user_id, balance=0.0)
            session.add(account)
            await session.flush() # Чтобы счет появился в БД до обновления баланса

        # 5. Сохранение транзакции и атомарное начисление баланса
        try:
            payment = Payment(
                transaction_id=data.transaction_id,
                user_id=data.user_id,
                account_id=data.account_id,
                amount=data.amount
            )
            session.add(payment)
            
            # Атомарное обновление баланса на уровне БД
            await session.execute(
                update(Account)
                .where(Account.id == account.id)
                .values(balance=Account.balance + data.amount)
            )
            
            await session.commit()
            return json({"message": "Payment processed successfully"}, 200)
            
        except IntegrityError:
            await session.rollback()
            return json({"message": "Transaction already processed"}, 200)