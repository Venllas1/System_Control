"""
Autodiagnóstico para Vercel - CABELAB 2025
Detecta problemas comunes de importación y configuración
"""
import sys
import os

print("=" * 60)
print("AUTODIAGNÓSTICO VERCEL - CABELAB 2025")
print("=" * 60)

# 1. Verificar estructura de directorios
print("\n[1] Verificando estructura de directorios...")
expected_dirs = ['app', 'app/blueprints', 'app/models', 'app/services', 'app/core']
for dir_path in expected_dirs:
    exists = os.path.isdir(dir_path)
    status = "✓" if exists else "✗"
    print(f"  {status} {dir_path}")

# 2. Verificar archivos críticos
print("\n[2] Verificando archivos críticos...")
critical_files = [
    'app/__init__.py',
    'app/extensions.py',
    'app/models/user.py',
    'app/models/equipment.py',
    'requirements.txt',
    'vercel.json'
]
for file_path in critical_files:
    exists = os.path.isfile(file_path)
    status = "✓" if exists else "✗"
    print(f"  {status} {file_path}")

# 3. Detectar conflicto de nombres
print("\n[3] Detectando conflictos de nombres...")
if os.path.isfile('app.py') and os.path.isdir('app'):
    print("  ✗ CONFLICTO DETECTADO: 'app.py' y directorio 'app/' coexisten")
    print("    → Esto causa importación circular en Python")
    print("    → SOLUCIÓN: Renombrar 'app.py' a 'wsgi.py' o 'server.py'")
else:
    print("  ✓ No se detectaron conflictos de nombres")

# 4. Intentar importación
print("\n[4] Probando importación del Factory...")
try:
    # Evitar el conflicto temporalmente
    sys.path.insert(0, os.path.abspath('.'))
    from app import create_app
    print("  ✓ Importación exitosa de create_app")
    
    # Intentar crear la app
    try:
        test_app = create_app()
        print("  ✓ Aplicación creada exitosamente")
    except Exception as e:
        print(f"  ✗ Error al crear aplicación: {e}")
        
except ImportError as e:
    print(f"  ✗ Error de importación: {e}")
    print("    → Verifica que app/__init__.py exporte create_app")

# 5. Verificar vercel.json
print("\n[5] Verificando configuración de Vercel...")
if os.path.isfile('vercel.json'):
    with open('vercel.json', 'r') as f:
        content = f.read()
        if 'app.py' in content:
            print("  ⚠ vercel.json apunta a 'app.py'")
            print("    → Debe actualizarse si se renombra el archivo")
        print(f"  Contenido actual:\n{content}")

print("\n" + "=" * 60)
print("FIN DEL DIAGNÓSTICO")
print("=" * 60)
