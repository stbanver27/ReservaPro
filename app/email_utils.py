"""
Envío de correos. Si SMTP_ENABLED = False o falla la conexión,
el sistema continúa sin error — solo registra el evento.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import (
    SMTP_ENABLED, SMTP_HOST, SMTP_PORT,
    SMTP_USER, SMTP_PASSWORD, EMAIL_FROM, EMAIL_FROM_NAME
)

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, html_body: str) -> bool:
    """
    Envía un correo HTML. Retorna True si fue enviado, False si falla o está desactivado.
    Nunca lanza una excepción al caller.
    """
    if not SMTP_ENABLED:
        logger.info(f"[Email desactivado] Para: {to} | Asunto: {subject}")
        return False

    if not to or "@" not in to:
        logger.warning(f"[Email] Dirección inválida: {to}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, [to], msg.as_string())

        logger.info(f"[Email] Enviado a {to}: {subject}")
        return True

    except Exception as e:
        logger.error(f"[Email] Error enviando a {to}: {e}")
        return False


def send_appointment_confirmation(client_email: str, client_name: str,
                                   service_name: str, professional_name: str,
                                   start_dt) -> bool:
    date_str = start_dt.strftime("%d/%m/%Y")
    time_str = start_dt.strftime("%H:%M")
    subject = f"Reserva confirmada — {service_name}"
    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 30px;">
      <h2 style="color: #2d6a4f;">✅ Tu reserva está confirmada</h2>
      <p>Hola <strong>{client_name}</strong>,</p>
      <p>Tu reserva ha sido registrada exitosamente:</p>
      <table style="border-collapse:collapse; width:100%; margin: 20px 0;">
        <tr><td style="padding:8px; background:#f0f0f0;"><strong>Servicio</strong></td>
            <td style="padding:8px;">{service_name}</td></tr>
        <tr><td style="padding:8px; background:#f0f0f0;"><strong>Profesional</strong></td>
            <td style="padding:8px;">{professional_name}</td></tr>
        <tr><td style="padding:8px; background:#f0f0f0;"><strong>Fecha</strong></td>
            <td style="padding:8px;">{date_str}</td></tr>
        <tr><td style="padding:8px; background:#f0f0f0;"><strong>Hora</strong></td>
            <td style="padding:8px;">{time_str}</td></tr>
      </table>
      <p style="color:#666; font-size:13px;">Si necesitas cancelar o reagendar, contáctanos directamente.</p>
      <p style="color:#2d6a4f; font-weight:bold;">— Equipo ReservaPro</p>
    </div>
    """
    return send_email(client_email, subject, html)
