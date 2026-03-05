from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.models import Category, Client, Setting

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acceso solo para administradores.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.order_by(User.created_at.desc()).all()
    categories = Category.query.all()
    clients = Client.query.filter_by(active=True).order_by(Client.name).all()
    settings = Setting.query.all()
    return render_template('admin/index.html', users=users, categories=categories, clients=clients, settings=settings)

# ── Users ──
@admin_bp.route('/users/new', methods=['POST'])
@login_required
@admin_required
def new_user():
    name = request.form['name']
    email = request.form['email'].strip().lower()
    password = request.form['password']
    role = request.form.get('role', 'operator')

    if User.query.filter_by(email=email).first():
        flash('Ya existe un usuario con ese email.', 'danger')
        return redirect(url_for('admin.index'))

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash(f'Usuario {name} creado correctamente.', 'success')
    return redirect(url_for('admin.index'))

@admin_bp.route('/users/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('No podés desactivarte a vos mismo.', 'danger')
        return redirect(url_for('admin.index'))
    user.active = not user.active
    db.session.commit()
    flash(f'Usuario {user.name} {"activado" if user.active else "desactivado"}.', 'info')
    return redirect(url_for('admin.index'))

@admin_bp.route('/users/<int:id>/role', methods=['POST'])
@login_required
@admin_required
def change_role(id):
    user = User.query.get_or_404(id)
    new_role = request.form.get('role')
    if new_role in ('admin', 'manager', 'operator'):
        user.role = new_role
        db.session.commit()
        flash(f'Rol de {user.name} cambiado a {new_role}.', 'success')
    return redirect(url_for('admin.index'))

# ── Categories ──
@admin_bp.route('/categories/new', methods=['POST'])
@login_required
@admin_required
def new_category():
    name = request.form.get('name', '').strip()
    if name:
        cat = Category(name=name)
        db.session.add(cat)
        db.session.commit()
        flash(f'Categoría "{name}" creada.', 'success')
    return redirect(url_for('admin.index'))

# ── Clients ──
@admin_bp.route('/clients/new', methods=['POST'])
@login_required
@admin_required
def new_client():
    client = Client(
        name=request.form['name'],
        email=request.form.get('email', ''),
        phone=request.form.get('phone', ''),
        ruc=request.form.get('ruc', ''),
        address=request.form.get('address', ''),
    )
    db.session.add(client)
    db.session.commit()
    flash(f'Cliente "{client.name}" creado.', 'success')
    return redirect(url_for('admin.index'))

# ── Settings ──
@admin_bp.route('/settings', methods=['POST'])
@login_required
@admin_required
def save_settings():
    keys = request.form.getlist('key[]')
    values = request.form.getlist('value[]')
    for k, v in zip(keys, values):
        s = Setting.query.filter_by(key=k).first()
        if s:
            s.value = v
        else:
            db.session.add(Setting(key=k, value=v))
    db.session.commit()
    flash('Configuración guardada.', 'success')
    return redirect(url_for('admin.index'))
