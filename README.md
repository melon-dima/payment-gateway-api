# Wallet API

Асинхронный REST API для управления кошельками на базе Sanic, SQLAlchemy и PostgreSQL.

## Возможности

- Аутентификация пользователей (JWT)
- Управление счетами и балансом
- Обработка платежей через webhooks
- Админ-панель для управления пользователями
- Идемпотентная обработка транзакций

## Требования

- Python 3.11+
- PostgreSQL 16+ (для локального запуска)
- Docker и Docker Compose (для запуска в контейнерах)

## Запуск через Docker

Самый простой способ — поднять приложение и базу данных одной командой:

```bash
docker compose up --build
```

После старта:

- API доступен по адресу: http://localhost:8000
- PostgreSQL доступен на порту `5432` (логин/пароль: `postgres` / `postgres`, БД: `wallet_db`)

Миграции Alembic применяются автоматически при запуске контейнера `app`.

Остановить сервисы:

```bash
docker compose down
```

Удалить данные PostgreSQL (volume):

```bash
docker compose down -v
```

### Переменные окружения

Все настройки хранятся в файле `.env` в корне проекта. Docker Compose автоматически читает этот файл и подставляет значения через синтаксис `${ИМЯ_ПЕРЕМЕННОЙ}`:

```yaml
POSTGRES_USER: ${POSTGRES_USER}
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

| Переменная | Описание |
|---|---|
| `POSTGRES_HOST` | Хост PostgreSQL (`localhost` для локального запуска) |
| `POSTGRES_PORT` | Порт PostgreSQL |
| `POSTGRES_USER` | Имя пользователя БД |
| `POSTGRES_PASSWORD` | Пароль БД |
| `POSTGRES_DB` | Имя базы данных |
| `SECRET_KEY` | Секрет для подписи JWT-токенов |
| `WEBHOOK_SECRET_KEY` | Секрет для проверки подписи webhook-запросов |
| `ALGORITHM` | Алгоритм JWT (по умолчанию `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access-токена в минутах |

Строка подключения к БД собирается автоматически из параметров `POSTGRES_*`.

При запуске через Docker сервис `app` подключается к БД по хосту `db` (имя сервиса в `docker-compose.yml`), а не `localhost` из `.env`.

## Запуск без Docker

### 1. Установить и запустить PostgreSQL

Создайте базу данных, например:

```sql
CREATE DATABASE wallet_db;
```

Убедитесь, что PostgreSQL слушает порт `5432`.

### 2. Создать файл `.env`

В корне проекта создайте файл `.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=wallet_db
SECRET_KEY=your_secret_key_here_for_jwt
WEBHOOK_SECRET_KEY=gfdmhghif38yrf9ew0jkf32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Для Docker достаточно заполнить `.env` — `docker compose` подхватит его автоматически. Хост БД (`POSTGRES_HOST=db`) для контейнера `app` переопределяется в `docker-compose.yml`.


### 3. Установить зависимости

С виртуальным окружением:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

Установка пакетов (через `uv`):

```bash
pip install uv
uv pip install .
```

Или через `pip`:

```bash
pip install .
```

### 4. Применить миграции

```bash
alembic upgrade head
```

### 5. Запустить приложение

```bash
python -m app.main
```

API будет доступен по адресу: http://localhost:8000

## Тестовые учётные данные

Создаются автоматически при миграции:

| Роль | Email | Пароль |
|---|---|---|
| Пользователь | `testuser@example.com` | `user123` |
| Администратор | `testadmin@example.com` | `admin123` |

## Тестирование API

Файл `api_curl.sh` — пошаговые `curl`-команды для ручной проверки API. Откройте файл и выполняйте команды по одной в bash-терминале, чтобы видеть реальные ответы сервера.

```bash
# Запустите API, затем откройте api_curl.sh и копируйте команды по порядку
docker compose up --build
```

После логина скопируйте `access_token` из ответа в переменную `USER_TOKEN` или `ADMIN_TOKEN` — дальнейшие команды используют их.

## API endpoints

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/auth/login` | Вход, получение JWT |
| `GET` | `/user/me` | Профиль текущего пользователя |
| `GET` | `/user/accounts` | Список счетов |
| `GET` | `/user/payments` | История платежей |
| `GET` | `/admin/me` | Профиль администратора |
| `GET` | `/admin/users` | Список пользователей |
| `POST` | `/admin/users` | Создание пользователя |
| `PUT` | `/admin/users/<id>` | Обновление пользователя |
| `DELETE` | `/admin/users/<id>` | Удаление пользователя |
| `POST` | `/webhook/payment` | Webhook для входящих платежей |

## Разработка

Установка dev-зависимостей:

```bash
uv pip install ".[dev]"
```

Запуск линтера:

```bash
ruff check .
```
