# notificaciones.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from models import Cita  # Asegúrate de que este modelo esté definido correctamente

# -------------------------------
# CONFIGURACIÓN SMTP (Correo)
# -------------------------------

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "kaelcraft@gmail.com"
SMTP_PASS = "tgxrtrbtlrakxzmf"

# -------------------------------
# CONFIGURACIÓN TWILIO (WhatsApp)
# -------------------------------

TWILIO_SID = "AC0f199cc91b27278de7bd2feb5d393fe4"
TWILIO_AUTH_TOKEN = "b2ec1f86370ce9745e2372a9ec1dd9a6"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

# SID del mensaje preaprobado en Twilio (Template en la consola)
TWILIO_TEMPLATE_SID = "HXb5b62575e6e4ff6129ad7c8efe1f983e"

# -------------------------------
# FUNCIÓN: Enviar Correo
# -------------------------------

def enviar_email(cita: Cita):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = cita.correo
    msg["Subject"] = f"Confirmación de cita #{cita.numero_ticket}"

    cuerpo = f"""
    Hola {cita.nombre},

    Tu cita ha sido registrada exitosamente para el día {cita.fecha} a las {cita.hora}.
    Dirección: {cita.direccion}
    Total a pagar: ${cita.total_pagar:.2f}

    Gracias por confiar en nosotros.
    """

    msg.attach(MIMEText(cuerpo, "plain"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, cita.correo, msg.as_string())
        print("✅ Correo enviado correctamente.")
    except Exception as e:
        print("❌ Error al enviar el correo:", e)

# -------------------------------
# FUNCIÓN: Enviar WhatsApp
# -------------------------------

def enviar_whatsapp(cita: Cita):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    content_variables = {
        "1": cita.fecha.strftime("%d/%m/%Y"),
        "2": cita.hora.strftime("%I:%M %p")
    }

    numero_destino = f"whatsapp:+57{cita.telefono}"

    print("🔍 Enviando WhatsApp a:", numero_destino)
    print("📦 Variables del template:", content_variables)
    print("📨 Desde:", TWILIO_WHATSAPP_NUMBER)

    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=numero_destino,
            content_sid=TWILIO_TEMPLATE_SID,
            content_variables=str(content_variables).replace("'", '"')
        )
        print("✅ WhatsApp enviado correctamente:", message.sid)
    except Exception as e:
        print("❌ Error al enviar WhatsApp:", e)
