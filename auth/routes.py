from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from dateutil.relativedelta import relativedelta
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # 1. Check Approval
            if not user.is_approved:
                flash('Tu cuenta está pendiente de aprobación por el administrador.', 'warning')
                return redirect(url_for('auth.login'))
            
            # 2. Check Expiration
            if user.expires_at and user.expires_at < datetime.utcnow():
                flash(f'Tu acceso expiró el {user.expires_at.strftime("%d/%m/%Y")}. Contacta al administrador ("Venllas").', 'danger')
                return redirect(url_for('auth.login'))
                
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Usuario o contraseña inválidos', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'danger')
        else:
            # First user is NOT auto-admin anymore (unless it's Venllas logic, handled separately)
            # Default: Not approved, Not admin
            user = User(username=username, is_admin=False, is_approved=False)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('Registro exitoso. Espera la aprobación del administrador.', 'info')
            return redirect(url_for('auth.login'))
            
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('index'))
        
    users = User.query.all()
    return render_template('auth/admin_users.html', users=users, now=datetime.utcnow())

@auth_bp.route('/admin/users/set_access/<int:user_id>', methods=['POST'])
@login_required
def set_access(user_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    user = User.query.get_or_404(user_id)
    meses = request.form.get('meses') # '1', '3', '6', '12', 'PERMANENT', 'BLOCK'
    
    if meses == 'BLOCK':
        user.is_approved = False
        user.expires_at = None
        flash(f'Usuario {user.username} bloqueado.', 'warning')
    elif meses == 'PERMANENT':
        user.is_approved = True
        user.expires_at = None
        flash(f'Acceso permanente otorgado a {user.username}.', 'success')
    else:
        try:
            if meses.endswith('h'):
                hours = int(meses[:-1])
                user.is_approved = True
                user.expires_at = datetime.utcnow() + relativedelta(hours=hours)
                flash(f'Acceso por {hours} horas otorgado a {user.username}. Expira: {user.expires_at.strftime("%d/%m %H:%M")}', 'success')
            else:
                months_to_add = int(meses)
                user.is_approved = True
                user.expires_at = datetime.utcnow() + relativedelta(months=months_to_add)
                flash(f'Acceso por {months_to_add} meses otorgado a {user.username}. Expira: {user.expires_at.strftime("%d/%m/%Y")}', 'success')
        except:
            flash('Opción no válida', 'danger')
    
    db.session.commit()
    return redirect(url_for('auth.admin_users'))

@auth_bp.route('/admin/users/toggle_admin/<int:user_id>')
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    if user_id == current_user.id:
        flash('No puedes quitarte tus propios permisos de admin', 'warning')
        return redirect(url_for('auth.admin_users'))
        
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'Permisos actualizados para {user.username}', 'success')
    return redirect(url_for('auth.admin_users'))

@auth_bp.route('/admin/users/set_role/<int:user_id>', methods=['POST'])
@login_required
def set_role(user_id):
    if not current_user.is_admin: # Solo admin puede cambiar roles
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role:
        user.role = new_role
        db.session.commit()
        flash(f'Rol de {user.username} actualizado a {new_role}', 'success')
    
    return redirect(url_for('auth.admin_users'))

@auth_bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Eliminar un usuario (solo admin)"""
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('index'))
    
    # No permitir eliminar a venllas
    user = User.query.get_or_404(user_id)
    if user.username.lower() == 'venllas':
        flash('No se puede eliminar al super administrador', 'danger')
        return redirect(url_for('auth.admin_users'))
    
    # No permitir auto-eliminación
    if user_id == current_user.id:
        flash('No puedes eliminarte a ti mismo', 'warning')
        return redirect(url_for('auth.admin_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Usuario {username} eliminado exitosamente', 'success')
    return redirect(url_for('auth.admin_users'))

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('La contraseña actual es incorrecta', 'danger')
            return redirect(url_for('auth.change_password'))
            
        if new_password != confirm_password:
            flash('Las nuevas contraseñas no coinciden', 'danger')
            return redirect(url_for('auth.change_password'))
            
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Tu contraseña ha sido actualizada exitosamente', 'success')
        return redirect(url_for('index'))
        
    return render_template('auth/change_password.html')
