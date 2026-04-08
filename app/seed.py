"""
Seed: pobla la base de datos con datos demo.
Ejecutar: python -m app.seed
"""
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.db.database import SessionLocal, create_tables
from app.models.user import User
from app.models.business import Business
from app.models.service import Service
from app.models.professional import Professional
from app.models.client import Client
from app.models.appointment import Appointment, AppointmentStatus
from app.core.config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_NAME

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed():
    create_tables()
    db = SessionLocal()

    try:
        # ── Admin ──────────────────────────────────────────────
        # Siempre regenera el hash para garantizar que sea válido
        hashed = pwd_context.hash(ADMIN_PASSWORD)
        existing_admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if existing_admin:
            existing_admin.hashed_password = hashed
            existing_admin.is_active = True
            existing_admin.is_admin = True
            db.commit()
            print(f"🔄 Admin actualizado: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        else:
            admin = User(
                name=ADMIN_NAME,
                email=ADMIN_EMAIL,
                hashed_password=hashed,
                is_active=True,
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            print(f"✅ Admin creado: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")

        # ── Negocio ────────────────────────────────────────────
        if not db.query(Business).first():
            biz = Business(
                name="Salón Belle Époque",
                address="Av. Providencia 1234, Santiago",
                phone="+56 9 8765 4321",
                email="contacto@belleepoque.cl",
                description="Salón de belleza y spa en el corazón de Providencia.",
                open_time="09:00",
                close_time="19:00",
                slot_duration=30,
            )
            db.add(biz)
            db.commit()
            print("✅ Negocio creado")

        # ── Servicios ──────────────────────────────────────────
        services_data = [
            ("Corte de cabello", "Corte personalizado para hombre o mujer", 30, 15000),
            ("Tinte completo", "Color completo con productos premium", 90, 45000),
            ("Mechas / Balayage", "Técnica de iluminación artesanal", 120, 60000),
            ("Manicure clásico", "Limpieza y esmaltado de manos", 45, 12000),
            ("Pedicure spa", "Tratamiento completo de pies", 60, 18000),
            ("Hidratación capilar", "Mascarilla y tratamiento nutritivo", 45, 20000),
            ("Alisado brasileño", "Alisado de larga duración", 150, 80000),
            ("Masaje relajante", "Masaje corporal 60 minutos", 60, 35000),
        ]
        existing_services = {s.name for s in db.query(Service).all()}
        created_services = []
        for name, desc, dur, price in services_data:
            if name not in existing_services:
                s = Service(name=name, description=desc, duration_minutes=dur, price=price, is_active=True)
                db.add(s)
                db.flush()
                created_services.append(s)
            else:
                created_services.append(db.query(Service).filter(Service.name == name).first())
        db.commit()
        # Refrescar para obtener IDs
        created_services = [db.query(Service).filter(Service.name == n).first() for n, *_ in services_data]
        print(f"✅ {len(services_data)} servicios verificados")

        # ── Profesionales ──────────────────────────────────────
        professionals_data = [
            ("Carolina Vásquez", "Colorista", "carolina@belleepoque.cl", "+56 9 1111 2222", "Especialista en color y técnicas de iluminación con 8 años de experiencia."),
            ("Rodrigo Muñoz", "Estilista", "rodrigo@belleepoque.cl", "+56 9 3333 4444", "Experto en cortes modernos y tendencias internacionales."),
            ("Valentina Torres", "Nail Artist", "valentina@belleepoque.cl", "+56 9 5555 6666", "Manicurista certificada, especialista en nail art y gel."),
            ("Andrés Soto", "Masajista", "andres@belleepoque.cl", "+56 9 7777 8888", "Terapeuta corporal con formación en técnicas orientales y occidentales."),
        ]
        existing_profs = {p.name for p in db.query(Professional).all()}
        for name, spec, email, phone, bio in professionals_data:
            if name not in existing_profs:
                p = Professional(
                    name=name, specialty=spec, email=email, phone=phone, bio=bio,
                    is_active=True, working_days="0,1,2,3,4",
                    work_start="09:00", work_end="18:00"
                )
                db.add(p)
        db.commit()
        created_profs = [db.query(Professional).filter(Professional.name == n).first() for n, *_ in professionals_data]
        print(f"✅ {len(professionals_data)} profesionales verificados")

        # ── Clientes ───────────────────────────────────────────
        clients_data = [
            ("María González", "maria.gonzalez@gmail.com", "+56 9 1234 5678"),
            ("Pedro Álvarez", "pedro.alvarez@hotmail.com", "+56 9 8765 4321"),
            ("Sofía Morales", "sofia.morales@gmail.com", "+56 9 2345 6789"),
            ("Camila Herrera", "camila.herrera@outlook.com", "+56 9 9876 5432"),
            ("Diego Ramírez", "diego.ramirez@gmail.com", "+56 9 3456 7890"),
            ("Javiera Pérez", "javiera.perez@gmail.com", "+56 9 6543 2109"),
        ]
        existing_clients_emails = {c.email for c in db.query(Client).all() if c.email}
        for name, email, phone in clients_data:
            if email not in existing_clients_emails:
                db.add(Client(name=name, email=email, phone=phone))
        db.commit()
        created_clients = [db.query(Client).filter(Client.email == e).first() for _, e, _ in clients_data]
        print(f"✅ {len(clients_data)} clientes verificados")

        # ── Reservas demo ──────────────────────────────────────
        if db.query(Appointment).count() == 0:
            now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
            appts_data = [
                (created_clients[0], created_profs[0], created_services[1], now + timedelta(days=1), AppointmentStatus.confirmed),
                (created_clients[1], created_profs[1], created_services[0], now + timedelta(days=1, hours=1), AppointmentStatus.confirmed),
                (created_clients[2], created_profs[2], created_services[3], now + timedelta(days=2), AppointmentStatus.pending),
                (created_clients[3], created_profs[3], created_services[7], now + timedelta(days=2, hours=2), AppointmentStatus.pending),
                (created_clients[4], created_profs[0], created_services[2], now + timedelta(days=3), AppointmentStatus.confirmed),
                (created_clients[5], created_profs[1], created_services[5], now - timedelta(days=1), AppointmentStatus.completed),
                (created_clients[0], created_profs[2], created_services[4], now - timedelta(days=2), AppointmentStatus.completed),
                (created_clients[1], created_profs[3], created_services[7], now - timedelta(days=3), AppointmentStatus.cancelled),
            ]
            for client, prof, service, start_dt, status in appts_data:
                if client and prof and service:
                    end_dt = start_dt + timedelta(minutes=service.duration_minutes)
                    db.add(Appointment(
                        client_id=client.id,
                        professional_id=prof.id,
                        service_id=service.id,
                        start_datetime=start_dt,
                        end_datetime=end_dt,
                        status=status,
                        price_charged=service.price,
                    ))
            db.commit()
            print(f"✅ {len(appts_data)} reservas demo creadas")

        print("\n🎉 Seed completado exitosamente")
        print(f"   👤 Admin: {ADMIN_EMAIL}")
        print(f"   🔑 Password: {ADMIN_PASSWORD}")
        print(f"   🌐 URL: http://localhost:8000")

    except Exception as e:
        db.rollback()
        print(f"❌ Error en seed: {e}")
        import traceback; traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
