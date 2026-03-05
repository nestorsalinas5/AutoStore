from flask import Blueprint, render_template
from flask_login import login_required
from app.models.models import Product, Invoice, PurchaseOrder, AutoAction, InvoiceItem
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    # KPIs
    sales_today = db.session.query(func.sum(Invoice.total)).filter(
        func.date(Invoice.created_at) == today,
        Invoice.status.in_(['paid', 'sent'])
    ).scalar() or 0

    sales_yesterday = db.session.query(func.sum(Invoice.total)).filter(
        func.date(Invoice.created_at) == today - timedelta(days=1),
        Invoice.status.in_(['paid', 'sent'])
    ).scalar() or 1

    sales_pct = round(((float(sales_today) - float(sales_yesterday)) / float(sales_yesterday)) * 100, 1)

    total_products = Product.query.filter_by(active=True).count()
    critical_products = Product.query.filter(
        Product.active == True,
        Product.stock <= Product.stock_min
    ).all()

    invoices_today = Invoice.query.filter(
        func.date(Invoice.created_at) == today
    ).count()

    pending_invoices_total = db.session.query(func.sum(Invoice.total)).filter(
        Invoice.status == 'pending'
    ).scalar() or 0

    # Weekly sales chart data (last 7 days)
    weekly_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        total = db.session.query(func.sum(Invoice.total)).filter(
            func.date(Invoice.created_at) == day,
            Invoice.status.in_(['paid', 'sent'])
        ).scalar() or 0
        weekly_data.append({'day': day.strftime('%a'), 'total': float(total)})

    # Recent invoices
    recent_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()

    # Recent auto actions
    auto_actions = AutoAction.query.order_by(AutoAction.created_at.desc()).limit(8).all()

    # Recent purchase orders
    recent_orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).limit(4).all()

    # Online vs Physical (mock split for now - can be extended)
    sales_week = db.session.query(func.sum(Invoice.total)).filter(
        func.date(Invoice.created_at) >= week_ago
    ).scalar() or 0

    return render_template('dashboard/index.html',
        sales_today=sales_today,
        sales_pct=sales_pct,
        total_products=total_products,
        critical_products=critical_products,
        invoices_today=invoices_today,
        pending_invoices_total=pending_invoices_total,
        weekly_data=weekly_data,
        recent_invoices=recent_invoices,
        auto_actions=auto_actions,
        recent_orders=recent_orders,
        sales_week=sales_week,
    )
