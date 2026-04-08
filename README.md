# ReservaPro 📅

Sistema de gestión de reservas y agenda para pequeños negocios (salones, clínicas, spas, etc.).  
Stack: **FastAPI · SQLAlchemy · SQLite/PostgreSQL · JWT · HTML/CSS/JS vanilla · Jinja2**

---

## Requisitos

- Python 3.10+
- pip

---

## Instalación y puesta en marcha

### 1. Clona o copia el proyecto

```bash
cd reservapro
```

### 2. Crea un entorno virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configura la aplicación

Edita `app/core/config.py` directamente. No uses `.env`.  
Los valores más importantes:

```python
DATABASE_URL  = "sqlite:///./reservapro.db"   # Cambia a PostgreSQL cuando quieras
SECRET_KEY    = "cambia-esta-clave..."         # Cámbiala en producción
ADMIN_EMAIL   = "admin@reservapro.cl"
ADMIN_PASSWORD= "Hola123"
```

### 5. Pobla la base de datos con datos demo

```bash
python -m app.seed
```

Esto crea:
- Usuario admin demo
- Negocio de ejemplo (Salón Belle Époque)
- 8 servicios
- 4 profesionales
- 6 clientes
- 8 reservas demo con distintos estados

### 6. Inicia el servidor

```bash
uvicorn app.main:app --reload
```

### 7. Abre en el navegador

| URL | Descripción |
|-----|-------------|
| http://localhost:8000 | Formulario público de reservas |
| http://localhost:8000/login | Login de administrador |
| http://localhost:8000/api/docs | Documentación interactiva (Swagger) |

### 8. Credenciales demo

```
Email:    admin@reservapro.cl
Password: admin123
```

---

## Estructura del proyecto

```
reservapro/
├── app/
│   ├── core/
│   │   └── config.py          ← Toda la configuración aquí
│   ├── db/
│   │   └── database.py        ← Engine SQLAlchemy
│   ├── models/                ← Modelos ORM
│   │   ├── user.py
│   │   ├── business.py
│   │   ├── service.py
│   │   ├── professional.py
│   │   ├── client.py
│   │   └── appointment.py
│   ├── schemas/               ← Pydantic schemas
│   ├── routers/               ← Endpoints FastAPI
│   │   ├── auth.py
│   │   ├── business.py
│   │   ├── services.py
│   │   ├── professionals.py
│   │   ├── clients.py
│   │   ├── appointments.py
│   │   └── public.py          ← Rutas HTML + API pública
│   ├── dependencies.py        ← JWT helpers
│   ├── email_utils.py         ← Envío de correos (no rompe si SMTP está off)
│   ├── seed.py                ← Datos demo
│   └── main.py                ← Punto de entrada
├── static/
│   ├── css/style.css
│   └── js/
│       ├── auth.js
│       ├── dashboard.js
│       ├── services.js
│       ├── professionals.js
│       ├── clients.js
│       ├── appointments.js
│       └── public.js
├── templates/                 ← Jinja2 HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── services.html
│   ├── professionals.html
│   ├── clients.html
│   ├── appointments.html
│   ├── business.html
│   └── public_booking.html
├── requirements.txt
└── README.md
```

---

## Funcionalidades

### Panel de administración

- **Dashboard** — KPIs (pendientes, confirmadas hoy, completadas del mes, ingresos)
- **Reservas** — CRUD completo, filtros por fecha y estado, selector de slots disponibles
- **Clientes** — CRUD, búsqueda en tiempo real
- **Servicios** — CRUD con duración y precio
- **Profesionales** — CRUD con horario laboral y días de trabajo
- **Negocio** — Configuración del establecimiento

### Formulario público

- Sin login requerido
- Selección de servicio, profesional y fecha
- Visualización de slots disponibles en tiempo real
- Creación automática de cliente si no existe
- Confirmación por correo (si SMTP está configurado)

### Reservas

- Validación de disponibilidad real (sin solapamientos)
- Estados: `pendiente`, `confirmada`, `cancelada`, `completada`
- Bloqueo automático de horarios ocupados

---

## Migrar a PostgreSQL

1. Instala el driver:
   ```bash
   pip install psycopg2-binary
   ```

2. En `app/core/config.py`, cambia:
   ```python
   DATABASE_URL = "postgresql://usuario:contraseña@localhost/reservapro"
   ```

3. Crea la base de datos en PostgreSQL y vuelve a ejecutar el seed:
   ```bash
   python -m app.seed
   ```

No necesitas cambiar ningún otro archivo.

---

## Activar envío de correos

En `app/core/config.py`:

```python
SMTP_ENABLED  = True
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587
SMTP_USER     = "tu@gmail.com"
SMTP_PASSWORD = "tu-app-password"
EMAIL_FROM    = "tu@gmail.com"
```

Si SMTP no está configurado o falla, el sistema continúa funcionando normalmente.

---

## Deploy en Railway

1. Sube el proyecto a GitHub
2. Crea un nuevo proyecto en Railway y conéctalo al repo
3. Agrega una base de datos PostgreSQL desde Railway
4. En `config.py` actualiza `DATABASE_URL` con la URL de Railway
5. Configura el comando de inicio:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
6. Ejecuta el seed una sola vez desde la terminal de Railway

---

## API — Endpoints principales

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/api/auth/login` | Obtener token JWT | No |
| GET | `/api/auth/me` | Usuario actual | Sí |
| GET | `/api/business` | Datos del negocio | No |
| PUT | `/api/business` | Actualizar negocio | Admin |
| GET | `/api/services` | Listar servicios | No |
| POST | `/api/services` | Crear servicio | Admin |
| PUT | `/api/services/{id}` | Actualizar servicio | Admin |
| DELETE | `/api/services/{id}` | Eliminar servicio | Admin |
| GET | `/api/professionals` | Listar profesionales | No |
| GET | `/api/clients` | Listar clientes | Admin |
| GET | `/api/appointments` | Listar reservas | Admin |
| GET | `/api/appointments/availability` | Slots disponibles | No |
| POST | `/api/appointments` | Crear reserva (admin) | Admin |
| PUT | `/api/appointments/{id}` | Actualizar estado | Admin |
| POST | `/api/public/book` | Reserva pública | No |

Documentación interactiva completa en: `http://localhost:8000/api/docs`

---

## Licencia

MIT — Libre para uso personal y comercial.
