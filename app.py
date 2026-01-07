"""
Aplicación Flask - CABELAB 2025 (SQL Version)
Sistema de Control de Equipos con Autenticación Local
"""
from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for, flash
from datetime import datetime, timedelta
import os
import pandas as pd
from sqlalchemy import or_, and_, case, func, text
import json

from config import Config
from extensions import db, login_manager
from models import User, Equipment, UserRoles
from auth.routes import auth_bp
from workflow_logic import validate_transition
from flask_login import current_user, login_required

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder.'
    login_manager.login_message_category = 'info'

    @app.route('/admin/db/backup')
    @login_required
    def backup_db():
        if not current_user.is_admin:
            flash('Acceso denegado', 'danger')
            return redirect(url_for('index'))
        
        db_path = os.path.join(app.root_path, 'cabelab.db')
        try:
            return send_file(db_path, as_attachment=True, download_name=f'backup_cabelab_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        except Exception as e:
            flash(f'Error al generar backup: {str(e)}', 'danger')
            return redirect(url_for('index'))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(auth_bp)

    @app.context_processor
    def inject_now():
        return {'now': datetime.now}


    @app.route('/')
    @login_required
    def index():
        """Vista principal del dashboard - Diferenciada por rol"""
        if current_user.role.lower() == UserRoles.VISUALIZADOR.lower():
            return redirect(url_for('panel_estados'))
            
        # ============================================
        # VISTA ADMIN - Estadísticas Globales
        # ============================================
        if current_user.role.lower() == 'admin':
            # Estadísticas completas
            total_equipos = Equipment.query.count()
            equipos_activos = Equipment.query.filter(
                ~Equipment.estado.in_(['Entregado', 'ENTREGADO'])
            ).count()
            
            # Equipos por estado
            equipos_por_estado = db.session.query(
                Equipment.estado, 
                func.count(Equipment.id)
            ).group_by(Equipment.estado).all()
            
            # Calcular equipos atrasados (más de 5 días sin cambio de estado)
            fecha_limite = datetime.now() - timedelta(days=5)
            equipos_atrasados = Equipment.query.filter(
                ~Equipment.estado.in_(['Entregado', 'ENTREGADO']),
                Equipment.fecha_ingreso < fecha_limite
            ).count()
            
            # Tiempo promedio de servicio (equipos entregados en últimos 30 días)
            fecha_30_dias = datetime.now() - timedelta(days=30)
            equipos_recientes = Equipment.query.filter(
                Equipment.estado.in_(['Entregado', 'ENTREGADO']),
                Equipment.fecha_ingreso >= fecha_30_dias
            ).all()
            
            if equipos_recientes:
                tiempos = [(datetime.now() - eq.fecha_ingreso).days for eq in equipos_recientes]
                tiempo_promedio = sum(tiempos) / len(tiempos)
            else:
                tiempo_promedio = 0
            
            # Equipos críticos (más de 7 días)
            fecha_critica = datetime.now() - timedelta(days=7)
            equipos_criticos = Equipment.query.filter(
                ~Equipment.estado.in_(['Entregado', 'ENTREGADO']),
                Equipment.fecha_ingreso < fecha_critica
            ).order_by(Equipment.fecha_ingreso.asc()).limit(5).all()
            
            # Todos los equipos para vista completa
            todos_equipos = Equipment.query.filter(
                ~Equipment.estado.in_(['Entregado', 'ENTREGADO'])
            ).order_by(Equipment.fecha_ingreso.desc()).all()
            
            stats_admin = {
                'total': total_equipos,
                'activos': equipos_activos,
                'atrasados': equipos_atrasados,
                'tiempo_promedio': round(tiempo_promedio, 1),
                'por_estado': dict(equipos_por_estado),
                'ultima_actualizacion': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
            return render_template('dashboard.html',
                                 is_admin_view=True,
                                 stats_admin=stats_admin,
                                 equipos_criticos=equipos_criticos,
                                 todos_equipos=todos_equipos,
                                 UserRoles=UserRoles,
                                 Status=Equipment.Status)
        
        # ============================================
        # VISTA USUARIOS - Solo Tareas Relevantes
        # ============================================
        else:
            # Filtrar equipos según rol
            equipos_relevantes = []
            user_role_norm = current_user.role.lower()
            
            if user_role_norm == UserRoles.OPERACIONES.lower():
                # Operaciones ve: equipos en diagnóstico, aprobados, en servicio
                equipos_relevantes = Equipment.query.filter(
                    db.or_(
                        Equipment.estado == Equipment.Status.ESPERA_DIAGNOSTICO,
                        Equipment.estado.in_(['en Diagnostico', 'DIAGNOSTICO']),
                        Equipment.estado == Equipment.Status.ESPERA_REPUESTO_CONSUMIBLE,
                        Equipment.estado == Equipment.Status.REPUESTO_ENTREGADO,
                        Equipment.estado.in_(['Aprobado', 'APROBADO']),
                        Equipment.estado == Equipment.Status.INICIO_SERVICIO,
                        Equipment.estado == Equipment.Status.EN_SERVICIO
                    )
                ).order_by(Equipment.fecha_ingreso.desc()).all()
            
            elif user_role_norm == UserRoles.RECEPCION.lower():
                # Recepción ve: equipos en espera de diagnóstico, pendientes de aprobación, culminados
                equipos_relevantes = Equipment.query.filter(
                    db.or_(
                        Equipment.estado == Equipment.Status.ESPERA_DIAGNOSTICO,
                        Equipment.estado == Equipment.Status.PENDIENTE_APROBACION,
                        Equipment.estado == Equipment.Status.SERVICIO_CULMINADO
                    )
                ).order_by(Equipment.fecha_ingreso.desc()).all()
            
            elif user_role_norm == UserRoles.ALMACEN.lower():
                # Almacén ve: equipos que esperan repuestos
                equipos_relevantes = Equipment.query.filter(
                    Equipment.estado.in_([
                        Equipment.Status.ESPERA_REPUESTO_CONSUMIBLE,
                        Equipment.Status.ESPERA_REPUESTOS
                    ])
                ).order_by(Equipment.fecha_ingreso.desc()).all()
            
            # Estadísticas simples para usuarios
            stats_user = {
                'mis_tareas': len(equipos_relevantes),
                'ultima_actualizacion': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
            return render_template('dashboard.html',
                                 is_admin_view=False,
                                 stats_user=stats_user,
                                 equipos_relevantes=equipos_relevantes,
                                 UserRoles=UserRoles,
                                 Status=Equipment.Status)

    @app.route('/panel')
    @login_required

    def panel_estados():
        """Panel visual de gestión de estados"""

        # Lógica de filtrado por rol para el panel
        # User REQ: Visualizador must see EVERYTHING (including Entregado)
        if current_user.role.lower() == UserRoles.VISUALIZADOR.lower():
            query = Equipment.query
        else:
            # For others, hide Entregado to keep panel clean
            query = Equipment.query.filter(~Equipment.estado.in_(['Entregado', 'ENTREGADO']))

        if current_user.role.lower() == UserRoles.OPERACIONES.lower():
            query = query.filter(or_(
                Equipment.estado == Equipment.Status.ESPERA_DIAGNOSTICO,
                Equipment.estado.in_(['en Diagnostico', 'DIAGNOSTICO']),
                Equipment.estado == Equipment.Status.ESPERA_REPUESTO_CONSUMIBLE,
                Equipment.estado == Equipment.Status.REPUESTO_ENTREGADO,
                Equipment.estado.in_(['Aprobado', 'APROBADO']),
                Equipment.estado == Equipment.Status.INICIO_SERVICIO,
                Equipment.estado == Equipment.Status.EN_SERVICIO
            ))
        elif current_user.role.lower() == UserRoles.RECEPCION.lower():
            query = query.filter(or_(
                Equipment.estado == Equipment.Status.ESPERA_DIAGNOSTICO,
                Equipment.estado == Equipment.Status.PENDIENTE_APROBACION,
                Equipment.estado == Equipment.Status.SERVICIO_CULMINADO
            ))
        elif current_user.role.lower() == UserRoles.ALMACEN.lower():
            query = query.filter(Equipment.estado.in_([
                Equipment.Status.ESPERA_REPUESTO_CONSUMIBLE,
                Equipment.Status.ESPERA_REPUESTOS
            ]))
        elif current_user.role.lower() == UserRoles.VISUALIZADOR.lower():
            # Visualizador ve todo lo activo (igual que admin, pero sin editar)
            pass 
        # Admin ve todo (ya filtrado Entregado arriba)

        equipments = query.order_by(Equipment.fecha_ingreso.desc()).all()
        
        # Convertir a JSON para JavaScript
        equipments_json = json.dumps([{
            'id': eq.id,
            'fr': eq.fr,
            'marca': eq.marca,
            'modelo': eq.modelo,
            'estado': eq.estado,
            'encargado': eq.encargado,
            'fecha_ingreso': eq.fecha_ingreso.strftime('%Y-%m-%d') if eq.fecha_ingreso else None
        } for eq in equipments])
        
        return render_template('panel_estados.html', 
                             equipments=equipments, 
                             equipments_json=equipments_json,
                             Status=Equipment.Status,
                             current_role=current_user.role)

    @app.route('/api/search')
    @login_required
    def search():
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': True, 'data': []})
        
        try:
            # Búsqueda optimizada SQL
            search_pattern = f"%{query}%"
            results = Equipment.query.filter(or_(
                Equipment.fr.ilike(search_pattern),
                Equipment.marca.ilike(search_pattern),
                Equipment.modelo.ilike(search_pattern),
                Equipment.encargado.ilike(search_pattern)
            )).limit(100).all()
            
            return jsonify({
                'success': True,
                'count': len(results),
                'data': [item.to_dict() for item in results]
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/stats')
    @login_required
    def get_stats():
        stats = {
            'diagnostico': Equipment.query.filter(Equipment.estado == Equipment.Status.EN_DIAGNOSTICO).count(),
            'aprobado': Equipment.query.filter(Equipment.estado == Equipment.Status.APROBADO).count(),
            'pendiente': Equipment.query.filter(Equipment.estado == Equipment.Status.PENDIENTE_APROBACION).count(),
            'total': Equipment.query.count() # Includes Entregado/Culminado for accuracy
        }
        stats['diagnostico_servicio'] = stats['diagnostico'] + stats['aprobado']
        return jsonify({'success': True, 'data': stats})

    @app.route('/api/refresh')
    @login_required
    def refresh_data():
        # User Request: Force sync when button is pressed
        from utils.excel_sync import sync_excel_to_db
        try:
            print("Manual Refresh: Forcing sync from Google Drive...")
            success = sync_excel_to_db(app, force=True)
            
            if success:
                return jsonify({
                    'success': True, 
                    'message': 'Datos actualizados correctamente desde Google Drive'
                })
            else:
               return jsonify({
                    'success': False, 
                    'message': 'No se pudo leer el Excel (Intente de nuevo)'
                }) 
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/export/<formato>')
    @login_required
    def export_data(formato):
        try:
            estado = request.args.get('estado', 'all')
            query = Equipment.query
            
            if estado == 'servicio':
                query = query.filter(or_(
                    Equipment.estado == Equipment.Status.EN_DIAGNOSTICO, 
                    Equipment.estado == Equipment.Status.APROBADO
                ))
            elif estado != 'all':
                query = query.filter(Equipment.estado == estado)
            
            items = query.all()
            data = [item.to_dict() for item in items]
            df = pd.DataFrame(data)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            os.makedirs('exports', exist_ok=True)
            
            if formato.lower() == 'csv':
                filename = f'export_{estado}_{timestamp}.csv'
                filepath = os.path.join('exports', filename)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                return send_file(filepath, as_attachment=True, download_name=filename)
            
            elif formato.lower() == 'excel':
                filename = f'export_{estado}_{timestamp}.xlsx'
                filepath = os.path.join('exports', filename)
                df.to_excel(filepath, index=False, engine='openpyxl')
                return send_file(filepath, as_attachment=True, download_name=filename)
            
            return jsonify({'success': False, 'error': 'Formato no soportado'}), 400
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
            return jsonify({'success': False, 'error': str(e)}), 500

    # ============================================
    # RUTAS DE GESTIÓN DE EQUIPOS (NUEVAS)
    # ============================================

    @app.route('/api/equipment/create', methods=['POST'])
    @login_required
    def create_equipment():
        # Regla: Solo RECEPCION (o Admin) puede crear
        if current_user.role.lower() != UserRoles.RECEPCION.lower() and current_user.role.lower() != UserRoles.ADMIN.lower():
             return jsonify({'success': False, 'error': 'No tiene permisos para registrar equipos (Solo Recepción).'}), 403
        
        try:
            data = request.get_json(silent=True) or request.form
            
            # Validar datos mínimos
            marca = data.get('marca')
            modelo = data.get('modelo')
            reporte = data.get('reporte_cliente')
            
            if not all([marca, modelo, reporte]):
                return jsonify({'success': False, 'error': 'Faltan campos obligatorios'}), 400
            
            # Date Logic
            fecha_str = data.get('fecha_ingreso')
            fecha_obj = datetime.now()
            if fecha_str:
                try:
                    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
                except:
                    pass # Fallback to now

            new_eq = Equipment(
                fr=data.get('fr', ''), 
                marca=marca,
                modelo=modelo,
                reporte_cliente=reporte,
                observaciones=data.get('observaciones', ''),
                condicion='Regular', # Default static since removed from UI
                encargado='No asignado', # Fixed default per User Request
                estado=Equipment.Status.ESPERA_DIAGNOSTICO, 
                # New Fields
                cliente=data.get('cliente', ''),
                serie=data.get('serie', ''),
                accesorios=data.get('accesorios', ''),
                fecha_ingreso=fecha_obj
            )
            
            db.session.add(new_eq)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Equipo registrado correctamente', 'id': new_eq.id})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/equipment/<int:eq_id>/update_status', methods=['POST'])
    @login_required
    def update_status(eq_id):
        equipment = Equipment.query.get_or_404(eq_id)
        
        # Obtenemos el nuevo estado deseado
        data = request.get_json(silent=True) or request.form
        new_status = data.get('status')
        observaciones = data.get('observaciones')
        new_encargado = data.get('encargado')
        
        if new_encargado:
            equipment.encargado = new_encargado
        
        if not new_status:
            return jsonify({'success': False, 'error': 'Nuevo estado no especificado'}), 400
            
        # VALIDAR TRANSICIÓN
        valid, error_msg = validate_transition(equipment.estado, new_status, current_user.role)
        
        # Override para Admin si es necesario (definido en workflow_logic, aqui solo consumimos)
        if not valid:
            return jsonify({'success': False, 'error': error_msg}), 403
            
        # Si es válido, aplicamos cambios
        equipment.estado = new_status
        if observaciones:
            # Append observaciones con timestamp
            timestamp = datetime.now().strftime('%d/%m %H:%M')
            old_obs = equipment.observaciones or ''
            equipment.observaciones = f"{old_obs}\n[{timestamp} {current_user.username}]: {observaciones}".strip()
            
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Estado actualizado a {new_status}',
            'new_status': new_status
        })

    @app.route('/api/equipment/<int:eq_id>/delete', methods=['POST'])
    @login_required
    def delete_equipment(eq_id):
        # SOLO ADMIN o VENLLAS
        if not current_user.is_admin and current_user.username != 'Venllas':
            return jsonify({'success': False, 'error': 'No autorizado'}), 403
            
        try:
            equipment = Equipment.query.get_or_404(eq_id)
            db.session.delete(equipment)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Equipo eliminado correctamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    def not_found_error(error):
        return render_template('error.html', mensaje="Página no encontrada"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('error.html', mensaje="Error interno del servidor"), 500

    return app

# Instancia para ejecución simple o WSGI
app = create_app()

# --- EXCEL SYNC THREAD & ROUTES (ADDED) ---
import threading
import time

def background_sync_task(app):
    """Syncs Excel every 15 minutes in background"""
    with app.app_context():
        while True:
            time.sleep(900) # 15 minutes
            print("Background Sync: Starting update from Google Drive...")
            try:
                from utils.excel_sync import sync_excel_to_db
                sync_excel_to_db(app)
            except Exception as e:
                print(f"Background Sync Error: {e}")

@app.route('/admin/sync_excel', methods=['POST'])
@login_required
def manual_sync_excel():
    if current_user.role not in [UserRoles.ADMIN, UserRoles.RECEPCION]:
        return jsonify({'success': False, 'error': 'No autorizado'}), 403
    
    try:
        from utils.excel_sync import sync_excel_to_db
        success = sync_excel_to_db(app)
        if success:
           return jsonify({'success': True, 'message': 'Sincronización completada.'})
        else:
           return jsonify({'success': False, 'error': 'Error al leer Google Drive.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/debug_sync')
def debug_sync_route():
    """Ruta de diagnóstico para ver logs de sincronización en tiempo real"""
    import io
    import sys
    from utils.excel_sync import sync_excel_to_db
    
    # Capture stdout
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    try:
        print("=== INICIANDO DEBUG SYNC ===")
        print(f"Hora: {datetime.now()}")
        
        # Run Sync (FORCE=True to bypass cooldown for debugging)
        result = sync_excel_to_db(app, force=True)
        
        print(f"\nResultado de Sincronización: {result}")
        
        # Check DB count
        count = Equipment.query.count()
        print(f"Total Equipos en DB: {count}")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
    # Restore stdout and return
    output = new_stdout.getvalue()
    sys.stdout = old_stdout
    
    return f"<pre style='background:#222; color:#0f0; padding:20px;'>{output}</pre>"

# --- VERCEL INITIALIZATION LOGIC ---
# Global flag to ensure we only init once per lambda instance
is_initialized = False

@app.before_request
def initialize_on_first_request():
    global is_initialized
    if not is_initialized:
        # Check if DB setup is needed (e.g. on Vercel cold boot)
        from sqlalchemy import inspect
        try:
            inspector = inspect(db.engine)
            # FORCE RE-CREATION OF EQUIPMENT TABLE to apply schema changes (String 50 -> 255)
            # Since data comes from Excel, this is safe and necessary.
            # Also create GlobalSettings if missing
            if not inspector.has_table("global_settings"):
                 db.create_all()
            
            # --- CRITICAL FIX: STOP DROPPING TABLE ---
            # The schema migration is done. Removing this to ensure persistence.
            # try:
            #     from models import Equipment
            #     Equipment.__table__.drop(db.engine, checkfirst=True)
            #     print("Vercel/Startup: Dropped Equipment table to update schema.")
            # except Exception as e:
            #     print(f"Schema Update Error: {e}")

            # --- AUTO-MIGRATE: Add new columns if missing ---
            try:
                # Use Inspector to check columns safely without breaking transactions
                columns = [c['name'] for c in inspector.get_columns('equipment')]
                
                with db.engine.connect() as conn:
                    if 'cliente' not in columns:
                        print("Migrating: Adding 'cliente' column...")
                        conn.execute(text("ALTER TABLE equipment ADD COLUMN cliente VARCHAR(255)"))
                        conn.commit()
                    
                    if 'serie' not in columns:
                        print("Migrating: Adding 'serie' column...")
                        conn.execute(text("ALTER TABLE equipment ADD COLUMN serie VARCHAR(255)"))
                        conn.commit()

                    if 'accesorios' not in columns:
                        print("Migrating: Adding 'accesorios' column...")
                        conn.execute(text("ALTER TABLE equipment ADD COLUMN accesorios TEXT"))
                        conn.commit()
            except Exception as e:
                print(f"Migration Logic Error: {e}")

            if not inspector.has_table("user"):
                print("Vercel/Startup: Initializing Database...")
                db.create_all()
            else:
                # If User exists but we dropped Equipment, we need to create Equipment again
                db.create_all() # safe, checks existence
                
                # Vercel/Native Mode: Users are persistent in Postgres.
                # Excel Sync is DISABLED to prevent data loss/overwrites.
                # db.create_all() checks are sufficient.
                
                # print("Vercel/Startup: Syncing from Google Drive...")
                # from utils.excel_sync import sync_excel_to_db
                # with app.app_context():
                #     sync_excel_to_db(app) # Initial Sync
                pass
                # Check for admin again
                if not User.query.filter_by(username='admin').first():
                    print("Vercel/Startup: Creating admin...")
                    u = User(username='admin', is_admin=True, is_approved=True)
                    u.set_password('admin123')
                    db.session.add(u)

                # Create Venllas (Reception/Admin?) - User requested "Venllas"
                if not User.query.filter_by(username='Venllas').first():
                    print("Vercel/Startup: Creating Venllas...")
                    # Assuming Venllas is generic Admin or Recepcion. Setting as Admin for safety based on previous context.
                    u = User(username='Venllas', role=UserRoles.ADMIN, is_admin=True, is_approved=True)
                    u.set_password('Venllas2025') # Default password
                    db.session.add(u)

                # Create Visualizador
                if not User.query.filter_by(username='visualizador').first():
                    print("Vercel/Startup: Creating visualizador...")
                    u = User(username='visualizador', role=UserRoles.VISUALIZADOR, is_approved=True)
                    u.set_password('visualizador123')
                    db.session.add(u)
                    
                db.session.commit()
            
            is_initialized = True
        except Exception as e:
            print(f"Startup Init Error: {e}")

if __name__ == '__main__':
    # Local Development Run
    with app.app_context():
        # Force init checks locally too
        initialize_on_first_request()
    
    # Start Background Thread (Only for local dev persistence)
    # Note: On Vercel this thread will die, but startup sync works on each cold boot.
    # We use daemon=True so it doesn't block shutdown
    sync_thread = threading.Thread(target=background_sync_task, args=(app,), daemon=True)
    sync_thread.start()

    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )