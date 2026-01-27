
import sys
import os
from sqlalchemy import text
from datetime import datetime

# Add parent dir to path to import app
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import create_app
from app.extensions import db

app = create_app()

def migrate():
    with app.app_context():
        print("Starting TIMESTAMP migration...")
        
        # We need to use proper casting for Postgres
        # For SQLite, it's more flexible but 'ALTER' doesn't support easy type changes.
        # However, for this project, Postgres (Neon) is the primary target.
        
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        is_postgres = db_uri.startswith('postgresql') or db_uri.startswith('postgres')
        
        with db.engine.connect() as conn:
            columns = ['hora_inicio_diagnostico', 'hora_inicio_mantenimiento']
            
            for col in columns:
                try:
                    if is_postgres:
                        # Convert VARCHAR to TIMESTAMP with explicit cast
                        query = text(f"ALTER TABLE equipment ALTER COLUMN {col} TYPE TIMESTAMP WITHOUT TIME ZONE USING {col}::timestamp WITHOUT TIME ZONE")
                        conn.execute(query)
                        print(f"Updated column {col} to TIMESTAMP (Postgres)")
                    else:
                        # SQLite doesn't support ALTER COLUMN TYPE. 
                        # But SQLite is dynamic, so we just let SQLAlchemy handle it as DateTime.
                        # If we really wanted to change it, we'd need to recreate the table.
                        print(f"Skipping type alteration for {col} on SQLite (dynamic typing)")
                except Exception as e:
                    print(f"Note on {col}: {str(e).splitlines()[0]}")
            
            conn.commit()
            print("Migration completed.")

if __name__ == '__main__':
    migrate()
