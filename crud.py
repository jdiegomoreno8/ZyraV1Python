from sqlalchemy.orm import Session
from models import Cita, Producto, Pago, Empresa
from schemas import CitaCreate
from datetime import datetime
import uuid  # Para generar el número de ticket


# ✅ Generador de ticket único
def generar_ticket():
    return f"TCK-{uuid.uuid4().hex[:8].upper()}"


# ✅ Crear una nueva cita con domicilio, productos, etc.
def crear_cita(db: Session, cita: CitaCreate):
    # Buscar el pago si se indicó
    pago = None
    if cita.id_pago:
        pago = db.query(Pago).filter(Pago.id_pago == cita.id_pago).first()

    # Buscar empresa si se indicó
    empresa = None
    if cita.id_empresa:
        empresa = db.query(Empresa).filter(Empresa.id_empresa == cita.id_empresa).first()

    # ✅ Crear nueva instancia de cita
    nueva = Cita(
        nombre=cita.nombre,
        apellido=cita.apellido,
        telefono=cita.telefono,
        correo=cita.correo,
        direccion=cita.direccion if cita.domicilio.lower() == 'si' else 'Recoge en tienda',
        domicilio=(cita.domicilio.lower() == 'si'),
        fecha=cita.fecha,
        hora=datetime.strptime(cita.hora, "%H:%M").time(),
        id_pago=cita.id_pago,
        id_empresa=cita.id_empresa,
        numero_ticket=cita.numero_ticket or generar_ticket(),
        cantidad_productos=len(cita.productos) if cita.productos else 0,

        # 🆕 Nuevos campos
        distancia_km=cita.distancia_km,
        costo_domicilio=cita.costo_domicilio
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    # ✅ Asociar productos si se enviaron
    if cita.productos:
        productos_objs = db.query(Producto).filter(Producto.id_producto.in_(cita.productos)).all()
        for prod in productos_objs:
            nueva.productos.append(prod)
        db.commit()
        db.refresh(nueva)

    return nueva
