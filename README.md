# 🚀 ReservaPro

Sistema moderno de gestión de reservas desarrollado con **FastAPI + SQLite**, diseñado para pequeñas y medianas empresas como peluquerías, centros estéticos, consultorios y servicios profesionales.

---

## ✨ Características

* 🔐 Autenticación con JWT
* 👤 Gestión de usuarios y roles
* 📅 Sistema de reservas
* 🗂️ Gestión de servicios
* ⏰ Control de horarios
* 📊 Dashboard con métricas básicas
* 🌐 Página pública de reservas
* 📄 Generación de tickets/resumen
* ⚡ Backend rápido con FastAPI

---

## 🛠️ Tecnologías

* FastAPI
* SQLAlchemy
* SQLite
* Jinja2
* Passlib + Bcrypt
* Uvicorn

---

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/stbanver27/ReservaPro.git
cd ReservaPro
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

Activar:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / Mac**

```bash
source venv/bin/activate
```

---

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuración

El sistema funciona en modo demo por defecto.

Puedes crear un archivo `.env` (opcional):

```env
SECRET_KEY=supersecretkey
SMTP_ENABLED=False
```

Si no configuras `.env`, el sistema igual funciona.

---

## ▶️ Ejecutar el proyecto

```bash
uvicorn app.main:app --reload
```

Abrir en navegador:

```
http://127.0.0.1:8000
```

---

## 🔑 Credenciales Demo

```txt
Email: admin@reservapro.cl
Password: Hola123
```

---

## 📁 Estructura del proyecto

```bash
app/
 ├── core/        # Configuración
 ├── models/      # Modelos DB
 ├── schemas/     # Validaciones
 ├── routes/      # Endpoints
 ├── services/    # Lógica de negocio
 ├── templates/   # HTML (Jinja2)
 └── main.py      # Entry point
```

---

## 📧 Sistema de correos

El envío de correos está desactivado por defecto:

```python
SMTP_ENABLED = False
```

En modo demo:

* No se envían correos reales
* Se simulan en consola

---

## ⚠️ Nota sobre bcrypt

Este proyecto fija:

```txt
bcrypt==4.0.1
```

Para evitar el error:

```
AttributeError: module 'bcrypt' has no attribute '__about__'
```

---

## 🚀 Roadmap

* [ ] Integración con pagos online
* [ ] Notificaciones por email reales
* [ ] Panel multi-sucursal
* [ ] API pública
* [ ] Deploy automático

---

## 📸 Capturas (próximamente)

Agrega aquí screenshots del sistema:

* Login
* Dashboard
* Agenda
* Reservas

---

## 🤝 Contribuciones

Este proyecto es open source.
Puedes hacer fork y mejorar funcionalidades.

---

## 📄 Licencia

MIT License

---

## 👨‍💻 Autor

Desarrollado por **Esteban Vergara**

---

## ⭐ Si te gusta el proyecto

Dale una estrella en GitHub ⭐
