from notificaciones import enviar_whatsapp
from datetime import date, time
from types import SimpleNamespace

# Simulamos una "Cita" como si fuera una instancia del modelo
cita_simulada = SimpleNamespace(
    nombre="Juan Pérez",
    fecha=date.today(),
    hora=time(15, 0),
    direccion="Carrera 45 #123",
    total_pagar=80000.00,
    telefono="3019420835",  # Sin el +57 porque ya lo agrega la función
    numero_ticket="TCK123",
    correo="cliente@ejemplo.com"
)

enviar_whatsapp(cita_simulada)
