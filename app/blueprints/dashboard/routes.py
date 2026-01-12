from flask import Blueprint, render_template, redirect, url_for, json
from flask_login import login_required, current_user
from app.services.equipment_service import EquipmentService
from app.models.user import UserRoles
from app.models.equipment import Equipment
from app.extensions import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    if current_user.role.lower() == UserRoles.VISUALIZADOR.lower():
        return redirect(url_for('dashboard.panel'))

    config = EquipmentService.get_dashboard_config(current_user)
    
    # Base Data
    data = {
        'stats': EquipmentService.get_admin_stats() if config['stats_visible'] else None,
        'equipments': EquipmentService.get_equipment_by_role(current_user),
        'history': EquipmentService.get_history() if 'history' in config['tables'] else [],
        'config': config
    }

    # Prepare JSON for JS tables
    entregados_json = json.dumps([eq.to_dict() for eq in data['history']])
    
    return render_template('dashboard.html', 
                         **data, 
                         entregados_json=entregados_json,
                         UserRoles=UserRoles,
                         Status=Equipment.Status)

@dashboard_bp.route('/panel')
@login_required
def panel():
    # Get all equipment for the user's role
    config = EquipmentService.get_dashboard_config(current_user)
    equipments = EquipmentService.get_equipment_by_role(current_user)
    
    # Group equipment by status
    diagnostico_equipos = [eq for eq in equipments if eq.estado == 'Espera de Diagnostico']
    aprobados_equipos = [eq for eq in equipments if eq.estado == 'Aprobado']
    servicio_equipos = [eq for eq in equipments if eq.estado == 'En Servicio']
    pendientes_equipos = [eq for eq in equipments if eq.estado == 'Pendiente de Aprobacion']
    
    # Calculate stats
    stats = {
        'diagnostico': len(diagnostico_equipos),
        'aprobados': len(aprobados_equipos) + len(servicio_equipos),
        'pendientes': len(pendientes_equipos),
        'total': len(equipments)
    }
    
    return render_template('panel_estados.html',
                         diagnostico_equipos=diagnostico_equipos,
                         aprobados_equipos=aprobados_equipos,
                         servicio_equipos=servicio_equipos,
                         pendientes_equipos=pendientes_equipos,
                         stats=stats,
                         Status=Equipment.Status,
                         current_role=current_user.role)

@dashboard_bp.route('/admin/db/backup')
@login_required
def backup_db():
    if not current_user.is_admin:
        return redirect(url_for('dashboard.index'))
    
    from flask import send_file, flash, current_app
    import os
    # Path relative to root where manage.py/app.py are
    db_path = os.path.join(current_app.root_path, 'cabelab.db')
    if os.path.exists(db_path):
        return send_file(db_path, as_attachment=True)
    flash("Base de datos no encontrada", "danger")
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/admin/import_informes', methods=['POST'])
@login_required
def import_informes():
    if not current_user.is_admin:
        return redirect(url_for('dashboard.index'))
    
    from flask import flash, request
    import csv
    import io

    file = request.files.get('file')
    if not file:
        flash('No se seleccionó archivo', 'danger')
        return redirect(url_for('dashboard.index'))

    try:
        content = file.read()
        try:
            stream = io.StringIO(content.decode('utf-8'))
        except UnicodeDecodeError:
            stream = io.StringIO(content.decode('latin-1'))
            
        reader = csv.DictReader(stream, delimiter=';')
        # Logic matches Step 402 implementation
        updated = 0
        for row in reader:
            fr = row.get('FR', '').strip().upper()
            informe = row.get('No DIAG', '').strip()
            if fr and informe:
                eq = Equipment.query.filter(Equipment.fr.ilike(fr)).first()
                if eq:
                    eq.numero_informe = informe
                    updated += 1
        db.session.commit()
        flash(f'Importación completada: {updated} equipos actualizados', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard.index'))
