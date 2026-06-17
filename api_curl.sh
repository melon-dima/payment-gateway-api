# =============================================================================
# Wallet API — ручное тестирование через curl
#
# Как пользоваться:
#   1. Запустите API (docker compose up --build  или  python -m app.main)
#   2. Откройте этот файл и выполняйте команды по одной в bash-терминале
#   3. После логина скопируйте access_token из ответа в переменную TOKEN
#
# Тестовые учётные данные (из миграции):
#   Пользователь:  testuser@example.com  / user123
#   Администратор: testadmin@example.com / admin123
# =============================================================================

export BASE_URL="http://localhost:8000"


# =============================================================================
# 1. ЛОГИН ПОЛЬЗОВАТЕЛЯ
# Ожидаемый ответ: {"access_token": "...", "token_type": "bearer"}
# =============================================================================

curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "user123"
  }'

# Скопируйте access_token из ответа и вставьте сюда:
export USER_TOKEN="ВСТАВЬТЕ_ТОКЕН_СЮДА"


# =============================================================================
# 2. ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
# Ожидаемый ответ: {"id": 1, "email": "testuser@example.com", "full_name": "Test User"}
# =============================================================================

curl "$BASE_URL/user/me" \
  -H "Authorization: Bearer $USER_TOKEN"


# =============================================================================
# 3. СЧЕТА ПОЛЬЗОВАТЕЛЯ
# Ожидаемый ответ: [{"id": 1, "balance": 0.0}]
# =============================================================================

curl "$BASE_URL/user/accounts" \
  -H "Authorization: Bearer $USER_TOKEN"


# =============================================================================
# 4. ПЛАТЕЖИ ПОЛЬЗОВАТЕЛЯ
# Ожидаемый ответ: []  (пустой список, если ещё не было пополнений)
# =============================================================================

curl "$BASE_URL/user/payments" \
  -H "Authorization: Bearer $USER_TOKEN"


# =============================================================================
# 5. WEBHOOK — ПОПОЛНЕНИЕ СЧЁТА (пример из ТЗ)
#
# Подпись считается так:
#   SHA256("{account_id}{amount}{transaction_id}{user_id}{secret_key}")
#
# Для этого примера secret_key = gfdmhghif38yrf9ew0jkf32
# Строка: 11005eae174f-7cd0-472c-bd36-35660f00132b1gfdmhghif38yrf9ew0jkf32
# Подпись:  7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8
#
# Ожидаемый ответ: {"message": "Payment processed successfully"}
# =============================================================================

curl -X POST "$BASE_URL/webhook/payment" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "user_id": 1,
    "account_id": 1,
    "amount": 100,
    "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
  }'


# =============================================================================
# 6. WEBHOOK — ПОВТОР ТОЙ ЖЕ ТРАНЗАКЦИИ (идемпотентность)
# Ожидаемый ответ: {"message": "Transaction already processed"}
# =============================================================================

curl -X POST "$BASE_URL/webhook/payment" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "user_id": 1,
    "account_id": 1,
    "amount": 100,
    "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
  }'


# =============================================================================
# 7. WEBHOOK — НОВОЕ ПОПОЛНЕНИЕ (нужна новая подпись)
#
# Сначала сгенерируйте подпись (подставьте свои значения):
# =============================================================================

python3 -c "
import hashlib
account_id = 1
amount = 50
transaction_id = 'my-new-transaction-001'
user_id = 1
secret_key = 'gfdmhghif38yrf9ew0jkf32'
raw = f'{account_id}{amount}{transaction_id}{user_id}{secret_key}'
print('Строка для хеша:', raw)
print('Подпись:', hashlib.sha256(raw.encode()).hexdigest())
"

# Затем отправьте webhook с полученной подписью:
curl -X POST "$BASE_URL/webhook/payment" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "my-new-transaction-001",
    "user_id": 1,
    "account_id": 1,
    "amount": 50,
    "signature": "ВСТАВЬТЕ_ПОДПИСЬ_ИЗ_КОМАНДЫ_ВЫШЕ"
  }'


# =============================================================================
# 8. WEBHOOK — НЕВЕРНАЯ ПОДПИСЬ
# Ожидаемый ответ: {"error": "Invalid signature"}  (HTTP 403)
# =============================================================================

curl -X POST "$BASE_URL/webhook/payment" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "bad-signature-test",
    "user_id": 1,
    "account_id": 1,
    "amount": 10,
    "signature": "wrong_signature"
  }'


# =============================================================================
# 9. СЧЕТА ПОСЛЕ ПОПОЛНЕНИЯ
# Ожидаемый ответ: [{"id": 1, "balance": 150.0}]  (100 + 50)
# =============================================================================

curl "$BASE_URL/user/accounts" \
  -H "Authorization: Bearer $USER_TOKEN"


# =============================================================================
# 10. ПЛАТЕЖИ ПОСЛЕ ПОПОЛНЕНИЯ
# =============================================================================

curl "$BASE_URL/user/payments" \
  -H "Authorization: Bearer $USER_TOKEN"


# =============================================================================
# 11. ЛОГИН АДМИНИСТРАТОРА
# =============================================================================

curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testadmin@example.com",
    "password": "admin123"
  }'

export ADMIN_TOKEN="ВСТАВЬТЕ_ТОКЕН_АДМИНА_СЮДА"


# =============================================================================
# 12. ПРОФИЛЬ АДМИНИСТРАТОРА
# =============================================================================

curl "$BASE_URL/admin/me" \
  -H "Authorization: Bearer $ADMIN_TOKEN"


# =============================================================================
# 13. СПИСОК ВСЕХ ПОЛЬЗОВАТЕЛЕЙ СО СЧЕТАМИ
# =============================================================================

curl "$BASE_URL/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN"


# =============================================================================
# 14. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ
# Ожидаемый ответ: {"id": 3, "email": "...", "full_name": "..."}  (HTTP 201)
# =============================================================================

curl -X POST "$BASE_URL/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "newpass123",
    "full_name": "New User",
    "is_admin": false
  }'


# =============================================================================
# 15. ОБНОВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ (замените 3 на id из ответа выше)
# =============================================================================

curl -X PUT "$BASE_URL/admin/users/3" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated User"
  }'


# =============================================================================
# 16. WEBHOOK — ПОПОЛНЕНИЕ НОВОГО СЧЁТА (счёт создаётся автоматически)
#
# Сгенерируйте подпись:
# =============================================================================

python3 -c "
import hashlib
account_id = 99
amount = 250
transaction_id = 'new-account-payment-001'
user_id = 3
secret_key = 'gfdmhghif38yrf9ew0jkf32'
raw = f'{account_id}{amount}{transaction_id}{user_id}{secret_key}'
print('Подпись:', hashlib.sha256(raw.encode()).hexdigest())
"

curl -X POST "$BASE_URL/webhook/payment" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "new-account-payment-001",
    "user_id": 3,
    "account_id": 99,
    "amount": 250,
    "signature": "ВСТАВЬТЕ_ПОДПИСЬ_ИЗ_КОМАНДЫ_ВЫШЕ"
  }'


# =============================================================================
# 17. УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ (замените 3 на id)
# Ожидаемый ответ: {"message": "User deleted"}
# =============================================================================

curl -X DELETE "$BASE_URL/admin/users/3" \
  -H "Authorization: Bearer $ADMIN_TOKEN"


# =============================================================================
# 18. ЗАПРОС БЕЗ ТОКЕНА
# Ожидаемый ответ: {"error": "Missing or invalid token"}  (HTTP 401)
# =============================================================================

curl "$BASE_URL/user/me"


# =============================================================================
# 19. ПОЛЬЗОВАТЕЛЬ ПЫТАЕТСЯ ЗАЙТИ В АДМИНКУ
# Ожидаемый ответ: {"error": "Admin privileges required"}  (HTTP 403)
# =============================================================================

curl "$BASE_URL/admin/users" \
  -H "Authorization: Bearer $USER_TOKEN"
