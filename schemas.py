# schemas.py
from pydantic import BaseModel, EmailStr
from datetime import date, datetime, time
from typing import List, Optional

# Producto base para incluir en otras respuestas
class ProductoBase(BaseModel):
    id_producto: int
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True

# Producto con cantidad en una cita (entrada)
class ProductoCantidad(BaseModel):
    id_producto: int
    cantidad: int

# Entrada al crear una cita (desde el frontend)
class CitaCreate(BaseModel):
    nombre: str
    apellido: str
    telefono: str
    correo: EmailStr
    direccion: str
    domicilio: str  # valores "si" o "no"
    fecha: date
    hora: str  # formato "HH:MM"
    id_pago: Optional[int] = None
    id_empresa: Optional[int] = None
    numero_ticket: Optional[str] = None
    #  Nuevos campos para cita con domicilio
    distancia_km: Optional[float] = None
    costo_domicilio: Optional[float] = None
    #  Esquema producto por cantidad
    productos: Optional[List[ProductoCantidad]] = []
    observaciones: Optional[str] = None
    metodo_envio: Optional[str] = None

# Producto dentro de una cita con precio
class ProductoEnCita(BaseModel):
    id_producto: int
    nombre: Optional[str]
    precio_unitario: float

    class Config:
        from_attributes = True



# Salida (respuesta cuando se guarda una cita)
class CitaRead(BaseModel):
    id: int
    nombre: str
    apellido: str
    telefono: str
    # correo: EmailStr
    correo: Optional[EmailStr] = None
    direccion: str
    domicilio: bool
    fecha: date
    hora: time
    id_pago: Optional[int]
    id_empresa: Optional[int]
    numero_ticket: Optional[str]
    cantidad_productos: Optional[int]
    productos: List[ProductoEnCita] = []
    distancia_km: Optional[float] = None
    costo_domicilio: Optional[float] = None
    valor_productos: Optional[float] = None
    total_pagar: Optional[float] = None
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


# Esquema para pagos (si se usa)
class PagoSchema(BaseModel):
    id_pago: int
    metodo: str   

    class Config:
        from_attributes = True


# Esquema para empresa
class EmpresaSchema(BaseModel):
    id_empresa: int
    nombre: str
    descripcion: Optional[str] = None
    direccion: Optional[str] = None

    class Config:
        from_attributes = True
class EmpresaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    direccion: Optional[str] = None


# Esquema completo para producto
class ProductoSchema(BaseModel):
    id_producto: int
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    cantidad_existente: Optional[int] = None

    class Config:
        from_attributes = True


# Empresa con productos (para vistas más complejas)
class EmpresaWithProductos(EmpresaSchema):
    productos: List[ProductoSchema] = []

    class Config:
        from_attributes = True

class CodigoCitaResponse(BaseModel):
    id_cita: int
    numero_ticket: str
    codigo_generado: str
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True