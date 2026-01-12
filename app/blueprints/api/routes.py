from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.equipment_service import EquipmentService
from app.core.permissions import role_required, can_perform_action

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/equipment/<int:id>/update_status', methods=['POST'])
@login_required
def update_status(id):
    if not can_perform_action(current_user, 'edit'):
        return jsonify({'success': False, 'error': 'Permiso denegado'}), 403
    
    new_status = request.form.get('status')
    new_encargado = request.form.get('encargado')
    
    if not new_status:
        return jsonify({'success': False, 'error': 'Falta el estado'}), 400
        
    success, message = EquipmentService.update_status(
        id, 
        new_status, 
        current_user.username, 
        encargado=new_encargado
    )
    
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'error': message}), 400

@api_bp.route('/equipment/<int:id>/details', methods=['GET'])
@login_required
def get_details(id):
    from app.models.equipment import Equipment
    eq = Equipment.query.get_or_404(id)
    return jsonify(eq.to_dict())
