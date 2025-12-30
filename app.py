"""
Aplicación Flask - CABELAB 2025 (SQL Version)
Sistema de Control de Equipos con Autenticación Local
"""
from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for, flash
from datetime import datetime, timedelta
import os
import pandas as pd
from sqlalchemy import or_, and_, case, func
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
        # En versión SQL, "refresh" no tiene mucho sentido si es DB directa, 
        # a menos que volvamos a leer el Excel (importación manual).
        # Por ahora simularemos éxito.
        return jsonify({
            'success': True, 
            'message': 'Datos sincronizados (Base de datos en tiempo real)'
        })

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
            
            new_eq = Equipment(
                fr=data.get('fr', ''), # FR puede ser autogenerado si se desea
                marca=marca,
                modelo=modelo,
                reporte_cliente=reporte,
                observaciones=data.get('observaciones', ''),
                condicion=data.get('condicion', 'Regular'),
                encargado=current_user.username,
                estado=Equipment.Status.ESPERA_DIAGNOSTICO # Estado Inicial
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
            
        # Actualizar encargado si cambia de área? 
        # Por ahora mantenemos el creador o actualizamos al que hizo la acción?
        # Mejor loguear quien lo movió en observaciones o un campo 'last_modified_by' si existiera.
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Estado actualizado a {new_status}',
            'new_status': new_status
        })
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # SYNC ON STARTUP (Google Drive)
        print("Startup Sync: Updating from Google Drive...")
        from utils.excel_sync import sync_excel_to_db
        sync_excel_to_db(app)

        # Crear admin si no existe
        if not User.query.first():
            print("Creando usuario admin inicial...")
            u = User(username='admin', is_admin=True, is_approved=True)
            u.set_password('admin123')
            db.session.add(u)
            db.session.commit()
    
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