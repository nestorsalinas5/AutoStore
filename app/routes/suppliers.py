from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.models import Supplier, PurchaseOrder, PurchaseOrderItem, Product, AutoAction, Invoice
from datetime import datetime

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

def next_po_number():
    last = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).first()
    n = (last.id + 1) if last else 1
    return f'OC-{n:05d}'

@suppliers_bp.route('/')
@login_required
def index():
    suppliers = Supplier.query.filter_by(active=True).order_by(Supplier.name).all()
    return render_template('suppliers/index.html', suppliers=suppliers)

@suppliers_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if not current_user.is_manager:
        flash('Sin permisos.', 'danger')
        return redirect(url_for('suppliers.index'))
    if request.method == 'POST':
        s = Supplier(
            name=request.form['name'],
            email=request.form.get('email', ''),
            phone=request.form.get('phone', ''),
            address=request.form.get('address', ''),
        )
        db.session.add(s)
        db.session.commit()
        flash(f'Proveedor "{s.name}" creado.', 'success')
        return redirect(url_for('suppliers.index'))
    return render_template('suppliers/form.html', supplier=None)

@suppliers_bp.route('/orders')
@login_required
def orders():
    orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).all()
    suppliers = Supplier.query.filter_by(active=True).all()
    products = Product.query.filter_by(active=True).all()
    return render_template('suppliers/orders.html', orders=orders, suppliers=suppliers, products=products)

@suppliers_bp.route('/orders/new', methods=['POST'])
@login_required
def new_order():
    supplier_id = request.form.get('supplier_id')
    product_ids = request.form.getlist('product_id[]')
    quantities = request.form.getlist('quantity[]')
    prices = request.form.getlist('unit_price[]')

    if not supplier_id or not product_ids:
        flash('Completá todos los campos.', 'danger')
        return redirect(url_for('suppliers.orders'))

    order = PurchaseOrder(
        number=next_po_number(),
        supplier_id=int(supplier_id),
        status='pending',
        auto_generated=False
    )
    db.session.add(order)
    db.session.flush()

    total = 0
    for pid, qty, price in zip(product_ids, quantities, prices):
        if not pid or not qty: continue
        qty = int(qty)
        price = float(price)
        subtotal = qty * price
        total += subtotal
        item = PurchaseOrderItem(order_id=order.id, product_id=int(pid), quantity=qty, unit_price=price, subtotal=subtotal)
        db.session.add(item)

    order.total = total
    action = AutoAction(type='purchase_order', description=f'Orden {order.number} creada por ₲ {total:,.0f}', status='ok')
    db.session.add(action)
    db.session.commit()
    flash(f'Orden {order.number} creada.', 'success')
    return redirect(url_for('suppliers.orders'))

@suppliers_bp.route('/orders/<int:id>/receive', methods=['POST'])
@login_required
def receive_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    order.status = 'received'
    order.received_at = datetime.utcnow()
    for item in order.items:
        item.product.stock += item.quantity
    action = AutoAction(type='stock_update', description=f'Stock actualizado por recepción de {order.number}', status='ok')
    db.session.add(action)
    db.session.commit()
    flash(f'Orden {order.number} recibida. Stock actualizado.', 'success')
    return redirect(url_for('suppliers.orders'))
