from app import create_app
from extensions import db
from sqlalchemy import text, inspect

def migrate():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('equipment')]
        
        # Columns to add: (Name, Type)
        # Note: TEXT works in Postgres. DATETIME maps to TIMESTAMP WITHOUT TIME ZONE in Postgres via SQLA, 
        # but for raw SQL usage, 'TIMESTAMP' is safer for Postgres, while 'DATETIME' is for SQLite.
        # However, Postgres also accepts 'TIMESTAMP'.
        
        is_sqlite = 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']
        
        new_columns = [
            ('fecha_fin_diagnostico', 'TIMESTAMP' if not is_sqlite else 'DATETIME'),
            ('observaciones_diagnostico', 'TEXT'),
            ('fecha_inicio_servicio', 'TIMESTAMP' if not is_sqlite else 'DATETIME'),
            ('observaciones_inicio_servicio', 'TEXT'),
            ('fecha_fin_servicio', 'TIMESTAMP' if not is_sqlite else 'DATETIME'),
            ('observaciones_fin_servicio', 'TEXT')
        ]

        with db.engine.connect() as conn:
            # We use a transaction
            trans = conn.begin()
            try:
                for col_name, col_type in new_columns:
                    if col_name not in existing_columns:
                        print(f"Adding column: {col_name} ({col_type})")
                        # Construct Query
                        # PostgreSQL supports "ADD COLUMN IF NOT EXISTS" but SQLite does not support "IF NOT EXISTS" in add column in older versions.
                        # Since we checked python-side "if col_name not in existing_columns", we can just use "ADD COLUMN".
                        sql = text(f'ALTER TABLE equipment ADD COLUMN "{col_name}" {col_type}')
                        conn.execute(sql)
                    else:
                        print(f"Column {col_name} already exists.")
                
                trans.commit()
                print("Migration successful!")
            except Exception as e:
                trans.rollback()
                print(f"Migration failed: {e}")
                raise e

if __name__ == '__main__':
    migrate()
