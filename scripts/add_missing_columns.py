
import sys
import os
from sqlalchemy import text

# Add parent dir to path to import app
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import create_app
from app.extensions import db

app = create_app()

def migrate():
    with app.app_context():
        print("Starting manual migration to add columns...")
        
        columns = [
            ("encargado_mantenimiento", "VARCHAR(255)"),
            ("hora_inicio_diagnostico", "VARCHAR(255)"),  # Using string for easier handling of various time formats in this legacy app
            ("observaciones_diagnostico", "TEXT"),
            ("hora_inicio_mantenimiento", "VARCHAR(255)"),
            ("observaciones_mantenimiento", "TEXT")
        ]
        
        with db.engine.connect() as conn:
            # Check if columns exist first (naive check or just try/except)
            # In SQLite adding columns is sometimes tricky, but for Postgres (Production) it's standard.
            # We'll use a try/except block for each column.
            
            for col_name, col_type in columns:
                try:
                    query = text(f"ALTER TABLE equipment ADD COLUMN {col_name} {col_type}")
                    conn.execute(query)
                    print(f"Added column: {col_name}")
                except Exception as e:
                    # Ignore if column likely exists
                    print(f"Skipping {col_name} (might exist): {str(e).splitlines()[0]}")
            
            conn.commit()
            print("Migration completed.")

if __name__ == '__main__':
    migrate()
