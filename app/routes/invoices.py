from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Invoice, InvoiceItem, Client, Product, AutoAction
from datetime import datetime, timedelta

invoices_bp = Blueprint('invoices', __name__, url_prefix='/invoices')

def next_invoice_number():
    last = Invoice.query.order_by(Invoice.id.desc()).first()
    n = (last.id + 1) if last else 1
    return f'F-{n:05d}'

@invoices_bp.route('/')
@login_required
def index():
    status = request.args.get('status', '')
    q = request.args.get('q', '')
    query = Invoice.query
    if status:
        query = query.filter_by(status=status)
    if q:
        query = query.join(Client).filter(Client.name.ilike(f'%{q}%') | Invoice.number.ilike(f'%{q}%'))
    invoices = query.order_by(Invoice.created_at.desc()).all()
    return render_template('invoices/index.html', invoices=invoices, status=status, q=q)

@invoices_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    clients = Client.query.filter_by(active=True).order_by(Client.name).all()
    products = Product.query.filter_by(active=True).order_by(Product.name).all()

    if request.method == 'POST':
        client_id = request.form.get('client_id')
        due_days = int(request.form.get('due_days', 30))
        notes = request.form.get('notes', '')
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('unit_price[]')

        if not client_id or not product_ids:
            flash('Seleccioná un cliente y al menos un producto.', 'danger')
            return render_template('invoices/form.html', clients=clients, products=products)

        invoice = Invoice(
            number=next_invoice_number(),
            client_id=int(client_id),
            status='pending',
            due_date=datetime.utcnow() + timedelta(days=due_days),
            notes=notes
        )
        db.session.add(invoice)
        db.session.flush()

        total = 0
        for pid, qty, price in zip(product_ids, quantities, prices):
            if not pid or not qty: continue
            qty = int(qty)
            price = float(price)
            subtotal = qty * price
            total += subtotal
            item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=int(pid),
                quantity=qty,
                unit_price=price,
                subtotal=subtotal
            )
            db.session.add(item)
            # Reduce stock
            product = Product.query.get(int(pid))
            if product:
                product.stock = max(0, product.stock - qty)

        invoice.total = total
        invoice.status = 'sent'

        # Log auto action
        action = AutoAction(
            type='invoice',
            description=f'Factura {invoice.number} emitida por ₲ {total:,.0f}',
            status='ok'
        )
        db.session.add(action)
        db.session.commit()

        flash(f'Factura {invoice.number} creada exitosamente.', 'success')
        return redirect(url_for('invoices.index'))

    return render_template('invoices/form.html', clients=clients, products=products)

@invoices_bp.route('/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    invoice = Invoice.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ('pending', 'sent', 'paid', 'overdue'):
        invoice.status = new_status
        if new_status == 'paid':
            invoice.paid_at = datetime.utcnow()
        db.session.commit()
        flash(f'Factura {invoice.number} marcada como {new_status}.', 'success')
    return redirect(url_for('invoices.index'))
