
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cabelab.db')

def add_column():
    print(f"Migrando base de datos en: {db_path}")
    if not os.path.exists(db_path):
        print("Error: No se encuentra el archivo de base de datos.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # Intentar añadir columna expires_at
        cur.execute("ALTER TABLE user ADD COLUMN expires_at DATETIME")
        print("Columna 'expires_at' agregada exitosamente.")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("La columna 'expires_at' ya existe.")
        else:
            print(f"Error SQL: {e}")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_column()
