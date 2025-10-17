# notificaciones.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from models import Cita  # Asegúrate de que este modelo esté definido correctamente
import os
from dotenv import load_dotenv

load_dotenv()
# -------------------------------
# CONFIGURACIÓN SMTP (Correo)
# -------------------------------

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID") 
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


# SID del mensaje preaprobado en Twilio (Template en la consola)
TWILIO_TEMPLATE_SID = "HXb5b62575e6e4ff6129ad7c8efe1f983e"

# -------------------------------
# FUNCIÓN: Enviar Correo
# -------------------------------

def enviar_email(cita: Cita, codigo: str):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = cita.correo
    msg["Subject"] = f"Confirmación de cita #{cita.numero_ticket}"

    cuerpo = f"""
    Hola {cita.nombre},

    Tu cita ha sido registrada exitosamente para el día {cita.fecha} a las {cita.hora}.
    Dirección: {cita.direccion}
    Total a pagar: ${cita.total_pagar:.2f}

      Tu código de verificación es: {codigo}
      (Este código guardalo porqué se necesita si deseas modificar tu pedido o cancelarlo)

    Gracias por confiar en nosotros.
    """

    msg.attach(MIMEText(cuerpo, "plain"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, cita.correo, msg.as_string())
        print("Correo enviado correctamente.")
    except Exception as e:
        print("Error al enviar el correo:", e)

# -------------------------------
# FUNCIÓN: Enviar SMS
# -------------------------------

def enviar_sms(cita: Cita, codigo: str):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    cuerpo_sms = (
        f"Hola {cita.nombre}, tu cita ha sido confirmada para el {cita.fecha.strftime('%d/%m/%Y')} "
        f"a las {cita.hora.strftime('%H:%M')}.\nDirección: {cita.direccion}.\n"
        f"Código de verificación: {codigo}\n"
        f"(Este código guárdalo porque se necesita si deseas modificar tu pedido o cancelarlo)\n"
        f"Total a pagar: ${cita.total_pagar:.2f}"
    )

    numero_destino = f"+57{cita.telefono}"

    try:
        message = client.messages.create(
            body=cuerpo_sms,
            from_="+15703644363",  # Usa tu número de Twilio SMS aquí
            to=numero_destino
        )
        print("✅ SMS enviado correctamente:", message.sid)
    except Exception as e:
        print("❌ Error al enviar SMS:", e)
