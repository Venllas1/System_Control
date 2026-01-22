from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app.models.equipment import Equipment
from app.services.equipment_service import EquipmentService
from app.core.permissions import role_required, can_perform_action

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/stats')
@login_required
def get_stats():
    # Parity with original monolithic app.py
    stats = {
        'diagnostico': Equipment.query.filter(Equipment.estado == Equipment.Status.EN_DIAGNOSTICO).count(),
        'aprobado': Equipment.query.filter(Equipment.estado == Equipment.Status.APROBADO).count(),
        'pendiente': Equipment.query.filter(Equipment.estado == Equipment.Status.PENDIENTE_APROBACION).count(),
        'total': Equipment.query.count()
    }
    stats['diagnostico_servicio'] = stats['diagnostico'] + stats['aprobado']
    return jsonify({'success': True, 'data': stats})

@api_bp.route('/equipment/<int:id>/update_status', methods=['POST'])
@login_required
def update_status(id):
    """
    Update equipment status with workflow validation.
    Validates transitions and role permissions through WorkflowEngine.
    
    Body:
        status: str - New status (must be valid transition)
        encargado: str (optional) - Assigned technician
    """
    if not can_perform_action(current_user, 'edit'):
        return jsonify({'success': False, 'error': 'Permiso denegado'}), 403
    
    try:
        # Accept both JSON and form data
        data = request.get_json(silent=True) or request.form
        new_status = data.get('status') or data.get('next_state')
        new_encargado = data.get('encargado')
        
        if not new_status:
            return jsonify({'success': False, 'error': 'Falta el estado'}), 400
        
        # Use workflow-validated method
        success, message, final_state = EquipmentService.advance_to_next_state(
            id, 
            current_user, 
            new_status
        )
        
        # Update encargado if provided
        if success and new_encargado:
            from app.models.equipment import Equipment
            from app.extensions import db
            equipment = Equipment.query.get(id)
            if equipment:
                equipment.encargado = new_encargado
                db.session.commit()
        
        if success:
            return jsonify({
                'success': True, 
                'message': message,
                'new_state': final_state
            })
        else:
            return jsonify({
                'success': False, 
                'error': message
            }), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/equipment/create', methods=['POST'])
@login_required
def create_equipment():
    if not can_perform_action(current_user, 'edit'):
        return jsonify({'success': False, 'error': 'Permiso denegado'}), 403
    
    data = request.get_json(silent=True) or request.form
    success, result = EquipmentService.create_equipment(data)
    
    if success:
        return jsonify({'success': True, 'id': result.id})
    return jsonify({'success': False, 'error': result}), 400

@api_bp.route('/equipment/<int:id>/details', methods=['GET'])
@login_required
def get_details(id):
    eq = Equipment.query.get_or_404(id)
    return jsonify(eq.to_dict())

@api_bp.route('/equipment/<int:id>/delete', methods=['POST'])
@login_required
def delete_equipment(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Solo administradores'}), 403
    
    if EquipmentService.delete_equipment(id):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'No encontrado'}), 404

@api_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    
    if not query or query == 'all':
        # Return all (limited to 500 recent) for general view
        results = Equipment.query.order_by(Equipment.fecha_ingreso.desc()).limit(500).all()
        return jsonify({
            'success': True, 
            'data': [item.to_dict() for item in results]
        })
        
    if not query:
        return jsonify({'success': True, 'data': []})
    
    results = EquipmentService.search(query)
    return jsonify({
        'success': True,
        'data': [item.to_dict() for item in results]
    })

@api_bp.route('/export/<formato>')
@login_required
def export_data(formato):
    import pandas as pd
    import os
    from flask import send_file
    
    try:
        estado = request.args.get('estado', 'all')
        query = Equipment.query
        if estado != 'all':
            query = query.filter(Equipment.estado == estado)
        
        items = query.all()
        df = pd.DataFrame([i.to_dict() for i in items])
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs('exports', exist_ok=True)
        filename = f'export_{estado}_{timestamp}.{formato}'
        filepath = os.path.join('exports', filename)
        
        if formato == 'csv':
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        else:
            df.to_excel(filepath, index=False)
            
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/pending_tasks')
@login_required
def get_pending_tasks():
    """
    Get equipment that requires action from the current user's role.
    Returns pending tasks ordered by priority (oldest first).
    """
    try:
        pending = EquipmentService.get_pending_tasks(current_user)
        return jsonify({
            'success': True,
            'data': [eq.to_dict() for eq in pending],
            'count': len(pending)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/equipment/<int:id>/next_state')
@login_required
def get_next_state(id):
    """
    Get information about the next possible state(s) for an equipment.
    Includes current state, next states, and user permissions.
    """
    try:
        info = EquipmentService.get_next_state_info(id, current_user)
        if not info:
            return jsonify({'success': False, 'error': 'Equipo no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/equipment/<int:id>/update_data', methods=['POST'])
@login_required
def update_equipment_data(id):
    """
    Update general equipment data (no status change).
    Allowed for roles with can_edit permission.
    """
    if not can_perform_action(current_user, 'edit'):
        return jsonify({'success': False, 'error': 'Permiso denegado'}), 403
    
    try:
        data = request.get_json(silent=True) or request.form
        success, message = EquipmentService.update_equipment_data(id, data)
        
        if success:
            return jsonify({'success': True, 'message': message})
        return jsonify({'success': False, 'error': message}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
