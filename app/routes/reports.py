from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app import db
from app.models.models import Product, Invoice, PurchaseOrder, AutoAction, InvoiceItem
from sqlalchemy import func
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    today = datetime.utcnow().date()

    # Sales last 30 days
    sales_30 = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        total = db.session.query(func.sum(Invoice.total)).filter(
            func.date(Invoice.created_at) == day,
            Invoice.status.in_(['paid', 'sent'])
        ).scalar() or 0
        sales_30.append({'day': day.strftime('%d/%m'), 'total': float(total)})

    # Top products by sales
    top_products = db.session.query(
        Product.name,
        func.sum(InvoiceItem.quantity).label('qty'),
        func.sum(InvoiceItem.subtotal).label('revenue')
    ).join(InvoiceItem).group_by(Product.id, Product.name).order_by(func.sum(InvoiceItem.subtotal).desc()).limit(8).all()

    # Invoice status breakdown
    status_counts = db.session.query(Invoice.status, func.count(Invoice.id)).group_by(Invoice.status).all()

    # Low stock products
    low_stock = Product.query.filter(Product.active == True, Product.stock <= Product.stock_min * 1.5).order_by(Product.stock).all()

    total_revenue = db.session.query(func.sum(Invoice.total)).filter(Invoice.status.in_(['paid', 'sent'])).scalar() or 0
    total_pending = db.session.query(func.sum(Invoice.total)).filter(Invoice.status == 'pending').scalar() or 0

    return render_template('reports/index.html',
        sales_30=sales_30,
        top_products=top_products,
        status_counts=status_counts,
        low_stock=low_stock,
        total_revenue=total_revenue,
        total_pending=total_pending,
    )


# ─── API Blueprint ───────────────────────────────────────────
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/products/critical')
@login_required
def critical_products():
    products = Product.query.filter(Product.active == True, Product.stock <= Product.stock_min).all()
    return jsonify([{'id': p.id, 'name': p.name, 'stock': p.stock, 'stock_min': p.stock_min} for p in products])

@api_bp.route('/actions/recent')
@login_required
def recent_actions():
    actions = AutoAction.query.order_by(AutoAction.created_at.desc()).limit(20).all()
    return jsonify([{
        'id': a.id,
        'type': a.type,
        'description': a.description,
        'status': a.status,
        'created_at': a.created_at.strftime('%H:%M')
    } for a in actions])

@api_bp.route('/dashboard/kpis')
@login_required
def kpis():
    today = datetime.utcnow().date()
    sales_today = db.session.query(func.sum(Invoice.total)).filter(
        func.date(Invoice.created_at) == today,
        Invoice.status.in_(['paid', 'sent'])
    ).scalar() or 0
    critical = Product.query.filter(Product.active == True, Product.stock <= Product.stock_min).count()
    return jsonify({'sales_today': float(sales_today), 'critical_stock': critical})
