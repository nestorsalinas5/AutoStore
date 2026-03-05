# 🏪 AutoStore — Sistema de Gestión con Piloto Automático

Sistema completo de gestión de negocio con inventario, facturación, proveedores, reportes, IA y panel de administración.

---

## 🚀 Deploy en Railway (recomendado — gratis)

### 1. Crear cuenta y proyecto
1. Ir a [railway.app](https://railway.app) y crear cuenta
2. Crear **New Project** → **Deploy from GitHub repo**
3. Subir este código a un repositorio de GitHub primero

### 2. Agregar base de datos PostgreSQL
1. En el proyecto Railway → **New** → **Database** → **Add PostgreSQL**
2. Railway crea la DB automáticamente y genera `DATABASE_URL`

### 3. Variables de entorno
En **Settings → Variables**, agregar:
```
SECRET_KEY=una-clave-muy-larga-y-aleatoria-aqui
FLASK_ENV=production
```
> `DATABASE_URL` se inyecta automáticamente por Railway desde la DB PostgreSQL.

### 4. Inicializar la base de datos
En el panel de Railway → **New** → **Run command**:
```
flask --app run seed
```

### 5. ¡Listo! Accedé al sistema
- **Email:** `admin@autostore.com`
- **Contraseña:** `admin123`
- ⚠️ **Cambiar la contraseña inmediatamente** desde el panel admin.

---

## 💻 Correr en local

### Requisitos
- Python 3.11+
- PostgreSQL instalado (o usar SQLite para pruebas)

### Instalación
```bash
# 1. Clonar y entrar al directorio
cd autostore

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus datos de PostgreSQL

# 5. Inicializar DB con datos demo
flask --app run seed

# 6. Correr el servidor
python run.py
```

Abrir http://localhost:5000

---

## 🔑 Roles de usuario

| Rol | Permisos |
|-----|----------|
| **Admin** | Todo: usuarios, clientes, categorías, configuración |
| **Manager** | Productos, facturas, órdenes de compra |
| **Operator** | Solo lectura + crear facturas |

---

## 📦 Módulos del sistema

- **Dashboard** — KPIs en tiempo real, gráficos de ventas, alertas
- **Inventario** — CRUD de productos, control de stock, alertas automáticas
- **Facturación** — Crear y gestionar facturas, actualiza stock automáticamente
- **Proveedores** — Gestión de proveedores y órdenes de compra
- **Reportes** — Gráficos de 30 días, top productos, estado de facturas
- **Administración** — Usuarios, roles, categorías, clientes (solo admin)

---

## 🛠️ Stack técnico

- **Backend:** Python 3.11 + Flask 3.0
- **Base de datos:** PostgreSQL + SQLAlchemy ORM
- **Auth:** Flask-Login con sesiones seguras
- **Frontend:** HTML/CSS/JS vanilla (sin dependencias externas)
- **Deploy:** Gunicorn + Railway/Render

---

## 📁 Estructura del proyecto

```
autostore/
├── run.py              # Entrypoint + comando seed
├── requirements.txt
├── Procfile            # Para Railway/Render
├── .env.example
└── app/
    ├── __init__.py     # App factory
    ├── models/
    │   ├── user.py     # Modelo de usuarios
    │   └── models.py   # Todos los demás modelos
    ├── routes/
    │   ├── auth.py
    │   ├── dashboard.py
    │   ├── inventory.py
    │   ├── invoices.py
    │   ├── suppliers.py
    │   ├── reports.py  # + api_bp
    │   └── admin.py
    └── templates/
        ├── base.html
        ├── auth/login.html
        ├── dashboard/index.html
        ├── inventory/
        ├── invoices/
        ├── suppliers/
        ├── reports/
        └── admin/
```
