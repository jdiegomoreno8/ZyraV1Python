from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import List, Optional

# Producto base para incluir en otras respuestas
class ProductoBase(BaseModel):
    id_producto: int
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


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
    productos: Optional[List[int]] = []  # IDs de productos seleccionados

    # 🆕 Nuevos campos para cita con domicilio
    distancia_km: Optional[float] = None
    costo_domicilio: Optional[float] = None


# Salida (respuesta cuando se guarda una cita)
class CitaRead(BaseModel):
    id: int
    nombre: str
    apellido: str
    telefono: str
    correo: EmailStr
    direccion: str
    domicilio: bool
    fecha: date
    hora: time
    id_pago: Optional[int]
    id_empresa: Optional[int]
    numero_ticket: Optional[str]
    cantidad_productos: Optional[int]
    productos: List[ProductoBase] = []

    # 🆕 Nuevos campos para ver el costo y distancia si aplica
    distancia_km: Optional[float] = None
    costo_domicilio: Optional[float] = None

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

    class Config:
        from_attributes = True


# Esquema completo para producto
class ProductoSchema(BaseModel):
    id_producto: int
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


# Empresa con productos (para vistas más complejas)
class EmpresaWithProductos(EmpresaSchema):
    productos: List[ProductoSchema] = []

    class Config:
        from_attributes = True
