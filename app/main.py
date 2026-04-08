from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import APP_NAME, APP_VERSION, ALLOWED_ORIGINS
from app.db.database import create_tables

from app.routers import auth, business, services, professionals, clients, appointments, public

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers API
app.include_router(auth.router)
app.include_router(business.router)
app.include_router(services.router)
app.include_router(professionals.router)
app.include_router(clients.router)
app.include_router(appointments.router)

# Rutas HTML públicas (siempre al final para no pisar las API)
app.include_router(public.router)


@app.on_event("startup")
def startup():
    create_tables()
    print(f"✅  {APP_NAME} v{APP_VERSION} iniciado")
    print("📄  Docs: http://localhost:8000/api/docs")
    print("🌐  App:  http://localhost:8000")
