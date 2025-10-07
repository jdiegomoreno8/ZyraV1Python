# crud.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Cita, Producto, Pago, Empresa, CitaProducto, CitaModificada, CitaAnulada
from schemas import CitaCreate
from datetime import datetime
from notificaciones import enviar_email, enviar_whatsapp
import uuid  # Para generar el número de ticket
import json

# Parsear la hora para manejas dos formatos
def parsear_hora(hora_str: str) -> datetime.time:
    formatos_validos = ["%H:%M:%S", "%H:%M"]
    for formato in formatos_validos:
        try:
            return datetime.strptime(hora_str, formato).time()
        except ValueError:
            continue
    raise HTTPException(
        status_code=400,
        detail=f"Formato de hora no válido: '{hora_str}'. Usa 'HH:MM' o 'HH:MM:SS'"
    )

# Generador de ticket único
def generar_ticket():
    return f"TCK-{uuid.uuid4().hex[:8].upper()}"

#  Crear una nueva cita con domicilio, productos, etc.
def crear_cita(db: Session, cita: CitaCreate):
    pago = db.query(Pago).filter(Pago.id_pago == cita.id_pago).first() if cita.id_pago else None
    empresa = db.query(Empresa).filter(Empresa.id_empresa == cita.id_empresa).first() if cita.id_empresa else None

    valor_productos = 0.0
    cantidad_total_productos = 0
    productos_detalle = {}
    productos_ids = [p.id_producto for p in cita.productos]

    if productos_ids:
        productos_detalle = {p.id_producto: p.cantidad for p in cita.productos}
        productos_objs = db.query(Producto).filter(Producto.id_producto.in_(productos_ids)).all()

        for prod in productos_objs:
            cantidad = productos_detalle.get(prod.id_producto, 0)

            # Validar stock
            if prod.cantidad_existente is not None and prod.cantidad_existente < cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"El producto '{prod.nombre}' no tiene suficiente stock. Disponible: {prod.cantidad_existente}, requerido: {cantidad}"
                )

            valor_productos += (prod.precio or 0.0) * cantidad
            cantidad_total_productos += cantidad

    costo_domicilio = cita.costo_domicilio if cita.domicilio.lower() == 'si' else 0.0
    total_pagar = valor_productos + (costo_domicilio or 0.0)

    nueva = Cita(
        nombre=cita.nombre,
        apellido=cita.apellido,
        telefono=cita.telefono,
        correo=cita.correo,
        direccion=cita.direccion if cita.domicilio.lower() == 'si' else 'Recoge en tienda',
        domicilio=(cita.domicilio.lower() == 'si'),
        fecha=cita.fecha,
        hora=parsear_hora(cita.hora),
        id_pago=cita.id_pago,
        id_empresa=cita.id_empresa,
        numero_ticket=cita.numero_ticket or generar_ticket(),
        cantidad_productos=cantidad_total_productos,
        distancia_km=cita.distancia_km,
        costo_domicilio=costo_domicilio,
        valor_productos=valor_productos,
        total_pagar=total_pagar,
        estado="activa",
        observaciones=cita.observaciones
    )

    db.add(nueva)
    db.flush()  # Se asegura de que nueva.id exista sin hacer commit todavía

    # Asociar productos con cantidad y descontar stock
    if productos_ids:
        for prod in productos_objs:
            cantidad = productos_detalle.get(prod.id_producto, 0)
            relacion = CitaProducto(
                id_cita=nueva.id,
                id_producto=prod.id_producto,
                cantidad=cantidad,
                precio_unitario=prod.precio
            )
            db.add(relacion)

            if prod.cantidad_existente is not None:
                prod.cantidad_existente -= cantidad

    db.commit()
    db.refresh(nueva)

    # Notificación al cliente según el método
    metodo = getattr(cita, "metodo_envio", None)
    if metodo == "correo":
        print("Enviando confirmación por correo...")
        enviar_email(nueva)
    elif metodo == "whatsapp":
        print("Enviando confirmación por WhatsApp...")
        enviar_whatsapp(nueva)
    else:
        print("No se especificó un método de envío válido.")

    print("Método de envío recibido:", metodo)

    return cita_a_dict(nueva)

#Función auxiliar qie convierte objeto Cita en diccionario de CitaRead
def cita_a_dict(cita: Cita) -> dict:
    productos_con_precios = [
        {
            "id_producto": cp.producto.id_producto,
            "nombre": cp.producto.nombre,
            "precio_unitario": cp.precio_unitario,
            "cantidad": cp.cantidad,
            "observaciones": cita.observaciones,
        }
        for cp in cita.cita_productos
    ]

    return {
        "id": cita.id,
        "nombre": cita.nombre,
        "apellido": cita.apellido,
        "telefono": cita.telefono,
        "correo": cita.correo,
        "direccion": cita.direccion,
        "domicilio": cita.domicilio,
        "fecha": cita.fecha,
        "hora": cita.hora,
        "id_pago": cita.id_pago,
        "id_empresa": cita.id_empresa,
        "numero_ticket": cita.numero_ticket,
        "cantidad_productos": cita.cantidad_productos,
        "productos": productos_con_precios,
        "distancia_km": cita.distancia_km,
        "costo_domicilio": cita.costo_domicilio,            
        "valor_productos": cita.valor_productos,
        "total_pagar": cita.total_pagar,
        "estado": cita.estado  # Nuevo campo
    }

def anular_cita(db: Session, cita_id: int, comentario: str):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    # Devolver stock
    for rel in cita.cita_productos:
        if rel.producto.cantidad_existente is not None:
            rel.producto.cantidad_existente += rel.cantidad

    # Cambiar estado
    cita.estado = "anulada"

    # Registrar anulación
    cita_anulada = CitaAnulada(
        id_cita=cita.id,
        comentario=comentario
    )

    db.add(cita_anulada)
    db.commit()
    return {"mensaje": "Cita anulada exitosamente", "id": cita.id}



# Modificar cita
def modificar_cita(db: Session, cita_id: int, datos: CitaCreate):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    #  Guardar copia previa en historial
    guardar_cita_modificada(db, cita)

    # --- Actualizar datos principales ---
    cita.nombre = datos.nombre
    cita.apellido = datos.apellido
    cita.telefono = datos.telefono
    cita.correo = datos.correo
    cita.direccion = datos.direccion if datos.domicilio.lower() == 'si' else 'Recoge en tienda'
    cita.domicilio = (datos.domicilio.lower() == 'si')
    cita.fecha = datos.fecha
    cita.hora = parsear_hora(datos.hora)
    cita.id_pago = datos.id_pago
    cita.id_empresa = datos.id_empresa
    cita.distancia_km = datos.distancia_km
    cita.costo_domicilio = datos.costo_domicilio if datos.domicilio.lower() == 'si' else 0.0

    # --- Resetear productos anteriores ---
    for rel in cita.cita_productos:
        # Devolver stock
        if rel.producto.cantidad_existente is not None:
            rel.producto.cantidad_existente += rel.cantidad
        db.delete(rel)

    db.flush()

    # --- Agregar los nuevos productos ---
    valor_productos = 0.0
    cantidad_total_productos = 0
    productos_detalle = {p.id_producto: p.cantidad for p in datos.productos}
    productos_objs = db.query(Producto).filter(Producto.id_producto.in_(productos_detalle.keys())).all()

    for prod in productos_objs:
        cantidad = productos_detalle.get(prod.id_producto, 0)

        if prod.cantidad_existente is not None and prod.cantidad_existente < cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"El producto '{prod.nombre}' no tiene suficiente stock. Disponible: {prod.cantidad_existente}, requerido: {cantidad}"
            )

        valor_productos += (prod.precio or 0.0) * cantidad
        cantidad_total_productos += cantidad

        relacion = CitaProducto(
            id_cita=cita.id,
            id_producto=prod.id_producto,
            cantidad=cantidad,
            precio_unitario=prod.precio
        )
        db.add(relacion)

        if prod.cantidad_existente is not None:
            prod.cantidad_existente -= cantidad

    # Totales y estado
    cita.cantidad_productos = cantidad_total_productos
    cita.valor_productos = valor_productos
    cita.total_pagar = valor_productos + (cita.costo_domicilio or 0.0)
    cita.estado = "modificada"

    db.commit()
    db.refresh(cita)
    return cita_a_dict(cita)

# Estados de la cita
def guardar_cita_modificada(db: Session, cita: Cita):
    datos = cita_a_dict(cita)  # Convertir a dict
    modificacion = CitaModificada(
        id_cita=cita.id,
        datos_anteriores=json.dumps(datos, default=str)
    )
    db.add(modificacion)

    from models import CitaAnulada

def guardar_cita_anulada(db: Session, cita: Cita, comentario: str = "Anulación desde sistema"):
    anulacion = CitaAnulada(
        id_cita=cita.id,
        comentario=comentario
    )
    db.add(anulacion)
