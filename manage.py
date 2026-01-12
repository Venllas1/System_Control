from app import create_app
from app.extensions import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist (Professional way)
        db.create_all()
    
    # In production, use Gunicorn instead of run()
    app.run(host='0.0.0.0', port=5000)
