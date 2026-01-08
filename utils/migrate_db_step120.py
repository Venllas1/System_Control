import sqlite3
import os

DB_PATH = r'cabelab.db'

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns_to_add = [
        ('fecha_fin_diagnostico', 'DATETIME'),
        ('observaciones_diagnostico', 'TEXT'),
        ('fecha_inicio_servicio', 'DATETIME'),
        ('observaciones_inicio_servicio', 'TEXT'),
        ('fecha_fin_servicio', 'DATETIME'),
        ('observaciones_fin_servicio', 'TEXT')
    ]

    print("Checking columns...")
    cursor.execute("PRAGMA table_info(equipment)")
    existing_cols = [row[1] for row in cursor.fetchall()]

    for col_name, col_type in columns_to_add:
        if col_name not in existing_cols:
            print(f"Adding column: {col_name}")
            try:
                cursor.execute(f"ALTER TABLE equipment ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")
        else:
            print(f"Column {col_name} already exists.")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
