from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.models import Product, Category, Supplier, AutoAction, PurchaseOrder, PurchaseOrderItem
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/')
@login_required
def index():
    q = request.args.get('q', '')
    category_id = request.args.get('category', '')
    status = request.args.get('status', '')

    query = Product.query.filter_by(active=True)
    if q:
        query = query.filter(Product.name.ilike(f'%{q}%') | Product.code.ilike(f'%{q}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status == 'critical':
        query = query.filter(Product.stock <= Product.stock_min)
    elif status == 'low':
        query = query.filter(Product.stock <= Product.stock_min * 1.5, Product.stock > Product.stock_min)

    products = query.order_by(Product.name).all()
    categories = Category.query.all()
    return render_template('inventory/index.html', products=products, categories=categories, q=q)

@inventory_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if not current_user.is_manager:
        flash('Sin permisos.', 'danger')
        return redirect(url_for('inventory.index'))

    categories = Category.query.all()
    suppliers = Supplier.query.filter_by(active=True).all()

    if request.method == 'POST':
        p = Product(
            code=request.form['code'],
            name=request.form['name'],
            description=request.form.get('description', ''),
            price_buy=float(request.form.get('price_buy', 0)),
            price_sell=float(request.form.get('price_sell', 0)),
            stock=int(request.form.get('stock', 0)),
            stock_min=int(request.form.get('stock_min', 10)),
            stock_max=int(request.form.get('stock_max', 100)),
            unit=request.form.get('unit', 'unidad'),
            category_id=request.form.get('category_id') or None,
            supplier_id=request.form.get('supplier_id') or None,
        )
        db.session.add(p)
        db.session.commit()
        flash(f'Producto "{p.name}" creado correctamente.', 'success')
        return redirect(url_for('inventory.index'))

    return render_template('inventory/form.html', product=None, categories=categories, suppliers=suppliers)

@inventory_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    if not current_user.is_manager:
        flash('Sin permisos.', 'danger')
        return redirect(url_for('inventory.index'))

    product = Product.query.get_or_404(id)
    categories = Category.query.all()
    suppliers = Supplier.query.filter_by(active=True).all()

    if request.method == 'POST':
        product.code = request.form['code']
        product.name = request.form['name']
        product.description = request.form.get('description', '')
        product.price_buy = float(request.form.get('price_buy', 0))
        product.price_sell = float(request.form.get('price_sell', 0))
        product.stock = int(request.form.get('stock', 0))
        product.stock_min = int(request.form.get('stock_min', 10))
        product.stock_max = int(request.form.get('stock_max', 100))
        product.unit = request.form.get('unit', 'unidad')
        product.category_id = request.form.get('category_id') or None
        product.supplier_id = request.form.get('supplier_id') or None
        product.updated_at = datetime.utcnow()
        db.session.commit()

        # Check if stock is critical after edit and log auto action
        if product.stock_status in ('critical', 'empty'):
            action = AutoAction(
                type='stock_alert',
                description=f'Stock crítico: {product.name} ({product.stock} unidades)',
                status='warning'
            )
            db.session.add(action)
            db.session.commit()

        flash(f'Producto "{product.name}" actualizado.', 'success')
        return redirect(url_for('inventory.index'))

    return render_template('inventory/form.html', product=product, categories=categories, suppliers=suppliers)

@inventory_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    if not current_user.is_admin:
        flash('Solo administradores pueden eliminar productos.', 'danger')
        return redirect(url_for('inventory.index'))
    product = Product.query.get_or_404(id)
    product.active = False
    db.session.commit()
    flash(f'Producto "{product.name}" desactivado.', 'info')
    return redirect(url_for('inventory.index'))
