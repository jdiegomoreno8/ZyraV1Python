from sqlalchemy.orm import Session
from models import Cita, Producto, Pago, Empresa
from schemas import CitaCreate
from datetime import datetime

def crear_cita(db: Session, cita: CitaCreate):
    # Obtener instancia de pago si se proporcionó, o crear si se requiere
    pago = None
    if cita.id_pago:
        pago = db.query(Pago).filter(Pago.id_pago == cita.id_pago).first()
    # opcional: podrías validar que exista, si no error

    empresa = None
    if cita.id_empresa:
        empresa = db.query(Empresa).filter(Empresa.id_empresa == cita.id_empresa).first()

    # Crear la cita
    nueva = Cita(
        nombre=cita.nombre,
        apellido=cita.apellido,
        telefono=cita.telefono,
        correo = cita.correo,
        direccion=cita.direccion if cita.domicilio.lower() == 'si' else 'Recoge en tienda',
        domicilio=(cita.domicilio.lower() == 'si'),
        fecha=cita.fecha,
        hora=datetime.strptime(cita.hora, "%H:%M").time(),
        id_pago = cita.id_pago,
        id_empresa = cita.id_empresa,
        numero_ticket = cita.numero_ticket,
        cantidad_productos = len(cita.productos) if cita.productos else 0
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    # Relacionar productos si se enviaron IDs
    if cita.productos:
        productos_objs = db.query(Producto).filter(Producto.id_producto.in_(cita.productos)).all()
        for prod in productos_objs:
            nueva.productos.append(prod)
        db.commit()
        db.refresh(nueva)

    return nueva
