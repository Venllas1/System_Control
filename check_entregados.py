"""
Script de diagnóstico para verificar equipos entregados en la base de datos
"""
from app import app, db, Equipment

with app.app_context():
    print("=" * 60)
    print("DIAGNÓSTICO: Equipos Entregados")
    print("=" * 60)
    
    # 1. Total de equipos
    total = Equipment.query.count()
    print(f"\n1. Total de equipos en BD: {total}")
    
    # 2. Todos los estados únicos
    estados = db.session.query(Equipment.estado).distinct().all()
    print(f"\n2. Estados únicos encontrados ({len(estados)}):")
    for estado in estados:
        count = Equipment.query.filter(Equipment.estado == estado[0]).count()
        print(f"   - '{estado[0]}' ({count} equipos)")
    
    # 3. Buscar con ilike('%entregado%')
    entregados = Equipment.query.filter(Equipment.estado.ilike('%entregado%')).all()
    print(f"\n3. Equipos con estado que contiene 'entregado' (case-insensitive): {len(entregados)}")
    
    if entregados:
        print("\n   Detalles:")
        for eq in entregados[:10]:  # Mostrar solo los primeros 10
            print(f"   - FR: {eq.fr}, Estado: '{eq.estado}', Marca: {eq.marca} {eq.modelo}")
    else:
        print("   ⚠️ NO SE ENCONTRARON EQUIPOS CON ESTADO 'ENTREGADO'")
        print("\n   Sugerencia: Verifica que existan equipos con estado 'Entregado' o 'ENTREGADO'")
        print("   en la base de datos. Puedes cambiar manualmente el estado de un equipo")
        print("   de prueba para verificar que la funcionalidad funciona correctamente.")
    
    # 4. Buscar variaciones comunes
    print("\n4. Buscando variaciones comunes:")
    variaciones = ['Entregado', 'ENTREGADO', 'entregado', 'Servicio culminado', 'SERVICIO CULMINADO']
    for var in variaciones:
        count = Equipment.query.filter(Equipment.estado == var).count()
        if count > 0:
            print(f"   - '{var}': {count} equipos")
    
    print("\n" + "=" * 60)
