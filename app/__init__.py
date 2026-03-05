import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')

    # Leer DATABASE_URL con múltiples fallbacks
   db_url = (
    os.environ.get('DATABASE_URL') or
    os.environ.get('POSTGRES_URL') or
    os.environ.get('POSTGRESQL_URL') or
    os.environ.get('PGDATABASE') or
    'sqlite:///autostore.db'
)
print(f">>> USANDO DB: {db_url[:30]}...", flush=True)

    # Railway/Render usan postgres:// pero SQLAlchemy necesita postgresql://
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    import logging
    logging.getLogger(__name__).info(f">>> DATABASE URL: {db_url}")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Iniciá sesión para acceder.'
    login_manager.login_message_category = 'warning'

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.inventory import inventory_bp
    from app.routes.invoices import invoices_bp
    from app.routes.suppliers import suppliers_bp
    from app.routes.reports import reports_bp, api_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    return app
