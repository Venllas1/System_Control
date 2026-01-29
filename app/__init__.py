from flask import Flask
from app.core.config import Config
from app.extensions import db, login_manager
from app.models.user import User

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', static_url_path='/static')
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
        from app.services.equipment_service import get_local_now
        from datetime import datetime
        return {'now': get_local_now, 'datetime': datetime}

    @app.before_request
    def ensure_db():
        # Vercel logic: Ensure tables and default users exist
        from app.models.user import User
        from app.extensions import db
        
        # Avoid repeated heavy checks
        if not getattr(app, '_db_initialized', False):
            try:
                # With context for safe execution
                with app.app_context():
                    db.create_all()
                    if not User.query.filter_by(username='admin').first():
                        u = User(username='admin', is_admin=True, role='admin', is_approved=True)
                        u.set_password('admin123')
                        db.session.add(u)
                    
                    if not User.query.filter_by(username='Venllas').first():
                        u = User(username='Venllas', is_admin=True, role='admin', is_approved=True)
                        u.set_password('Venllas2025')
                        db.session.add(u)
                    
                    db.session.commit()
                app._db_initialized = True
            except Exception as e:
                app.logger.error(f"AUTO-INIT ERROR: {str(e)}")

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        return render_template('500.html'), 500

    return app
