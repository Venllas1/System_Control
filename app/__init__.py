from flask import Flask
from app.core.config import Config
from app.extensions import db, login_manager
from app.models.user import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.dashboard.routes import dashboard_bp
    from app.blueprints.api.routes import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.now}

    @app.before_request
    def ensure_db():
        # Vercel logic: Ensure tables and default users exist
        from app.models.user import User, UserRoles
        from app.extensions import db
        
        # We use a static flag to avoid repeated checks per request
        if not getattr(app, '_db_initialized', False):
            try:
                db.create_all()
                if not User.query.filter_by(username='admin').first():
                    u = User(username='admin', is_admin=True, role='admin')
                    u.set_password('admin123')
                    db.session.add(u)
                
                if not User.query.filter_by(username='Venllas').first():
                    u = User(username='Venllas', is_admin=True, role='admin')
                    u.set_password('Venllas2025')
                    db.session.add(u)
                
                db.session.commit()
                app._db_initialized = True
            except Exception as e:
                print(f"Init DB Error: {e}")

    return app
