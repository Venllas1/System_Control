from flask import Blueprint, render_template, redirect, url_for, json
from flask_login import login_required, current_user
from app.services.equipment_service import EquipmentService
from app.models.user import UserRoles
from app.models.equipment import Equipment

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
    # Similar logic for Panel de Estados
    config = EquipmentService.get_dashboard_config(current_user)
    equipments = EquipmentService.get_equipment_by_role(current_user)
    
    # Convert to JSON for the existing JS logic in panel_estados.html
    equipments_json = json.dumps([eq.to_dict() for eq in equipments])
    
    return render_template('panel_estados.html',
                         equipments=equipments,
                         equipments_json=equipments_json,
                         Status=Equipment.Status,
                         current_role=current_user.role)
