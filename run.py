from app import create_app, db
from app.models.user import User
from app.models.models import Category, Supplier, Product, Client, Setting

app = create_app()

# Crear tablas automáticamente al arrancar
with app.app_context():
    db.create_all()
    
    # Crear admin si no existe
    if not User.query.filter_by(email='admin@autostore.com').first():
        admin = User(name='Administrador', email='admin@autostore.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin creado.", flush=True)
    else:
        print("✅ DB lista.", flush=True)

@app.cli.command('seed')
def seed():
    """Populate the database with demo data."""
    with app.app_context():
        db.create_all()
        # Categories
        cats = ['Electrónica', 'Accesorios', 'Impresión', 'Audio', 'Software']
        cat_objs = {}
        for c in cats:
            cat = Category.query.filter_by(name=c).first()
            if not cat:
                cat = Category(name=c)
                db.session.add(cat)
            cat_objs[c] = cat
        db.session.flush()

        suppliers_data = [
            ('TechDistrib PY', 'ventas@techdistrib.com.py', '021-123456'),
            ('Oficentro SRL', 'pedidos@oficentro.com.py', '021-654321'),
            ('Logitech Distrib', 'logitech@distrib.com', '021-999888'),
        ]
        sup_objs = {}
        for name, email, phone in suppliers_data:
            s = Supplier.query.filter_by(name=name).first()
            if not s:
                s = Supplier(name=name, email=email, phone=phone)
                db.session.add(s)
            sup_objs[name] = s
        db.session.flush()

        products_data = [
            ('NB-HP15', 'Notebook HP 15"', 2800000, 3500000, 15, 5, 30, 'Electrónica', 'TechDistrib PY'),
            ('MS-LG185', 'Mouse Logitech M185', 55000, 90000, 45, 10, 100, 'Accesorios', 'Logitech Distrib'),
            ('TN-CN047', 'Tóner Canon 047', 110000, 180000, 4, 5, 50, 'Impresión', 'Oficentro SRL'),
            ('KB-CK70', 'Teclado Mecánico K70', 380000, 550000, 20, 5, 40, 'Accesorios', 'TechDistrib PY'),
            ('MN-SS24', 'Monitor Samsung 24"', 950000, 1300000, 8, 3, 20, 'Electrónica', 'TechDistrib PY'),
        ]
        for code, name, buy, sell, stock, smin, smax, cat_name, sup_name in products_data:
            if not Product.query.filter_by(code=code).first():
                p = Product(
                    code=code, name=name, price_buy=buy, price_sell=sell,
                    stock=stock, stock_min=smin, stock_max=smax,
                    category=cat_objs.get(cat_name),
                    supplier=sup_objs.get(sup_name)
                )
                db.session.add(p)

        clients_data = [
            ('Grupo IT SA', 'compras@grupoit.com.py', '021-111222', '80012345-6'),
            ('Consultora ABC', 'admin@abc.com.py', '021-333444', '80054321-0'),
        ]
        for name, email, phone, ruc in clients_data:
            if not Client.query.filter_by(email=email).first():
                db.session.add(Client(name=name, email=email, phone=phone, ruc=ruc))

        db.session.commit()
        print("✅ Datos demo cargados.", flush=True)

if __name__ == '__main__':
    app.run(debug=False)
```

Y en Railway **borrá el Pre-deploy Command** (dejalo vacío). El Start Command queda igual:
```
gunicorn run:app --bind 0.0.0.0:$PORT
