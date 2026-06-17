from sanic import Sanic
from app.routes.auth import auth_bp
from app.routes.user import user_bp
from app.routes.admin import admin_bp
from app.routes.webhook import webhook_bp

app = Sanic("WalletAPI")
# app.config.CORS_ORIGINS = "*" # Раскомментировать, если нужен CORS

app.blueprint(auth_bp)
app.blueprint(user_bp)
app.blueprint(admin_bp)
app.blueprint(webhook_bp)

@app.before_server_start
async def setup_db(app, loop):
    # В продакшене таблицы создаются через Alembic.
    # Здесь мы просто убеждаемся, что движок инициализирован.
    pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True, auto_reload=True)