# test_email.py

from notificaciones import enviar_email
from datetime import date, time
from types import SimpleNamespace

# Simula una "Cita" como si fuera una instancia de tu modelo
cita_simulada = SimpleNamespace(
    nombre="Juan Pérez",
    fecha=date.today(),
    hora=time(14, 30),
    direccion="Calle 123 #45-67",
    total_pagar=75000.00,
    numero_ticket="TCK-EMAIL01",
    correo="kaelcraft@gmail.com"  # 👈 Cambia esto por un correo tuyo real para probar
)

# Ejecuta el envío del correo
enviar_email(cita_simulada)
