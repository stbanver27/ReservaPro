# ============================================================
# ReservaPro — Configuración central
# Edita este archivo directamente. Sin .env, sin os.getenv.
# ============================================================

# Base de datos
DATABASE_URL = "sqlite:///./reservapro.db"
# Para PostgreSQL, cambia a:
# DATABASE_URL = "postgresql://usuario:contraseña@localhost/reservapro"

# JWT
SECRET_KEY = "cambia-esta-clave-secreta-en-produccion-32-chars-min"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas

# App
APP_NAME = "ReservaPro"
APP_VERSION = "1.0.0"
DEBUG = True

# Admin demo (usado en seed)
ADMIN_EMAIL = "admin@reservapro.cl"
ADMIN_PASSWORD = "Hola123"
ADMIN_NAME = "Administrador"

# Email (opcional — si no está configurado, el sistema sigue funcionando)
SMTP_ENABLED = False          # Cambia a True y completa los datos para activar correos
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASSWORD = ""
EMAIL_FROM = "noreply@reservapro.cl"
EMAIL_FROM_NAME = "ReservaPro"

# Horario de atención por defecto
DEFAULT_OPEN_HOUR = 9    # 09:00
DEFAULT_CLOSE_HOUR = 19  # 19:00
SLOT_DURATION_MINUTES = 30

# CORS (orígenes permitidos)
ALLOWED_ORIGINS = ["*"]
