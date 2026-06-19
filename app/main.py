from sanic import Sanic
from app.routes.auth import auth_bp
from app.routes.user import user_bp
from app.routes.admin import admin_bp
from app.routes.webhook import webhook_bp

app = Sanic("WalletAPI")

app.blueprint(auth_bp)
app.blueprint(user_bp)
app.blueprint(admin_bp)
app.blueprint(webhook_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True, auto_reload=True)