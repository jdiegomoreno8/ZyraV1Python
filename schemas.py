from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import List, Optional

class ProductoBase(BaseModel):
    id_producto: int
    descripcion: Optional[str] = None

class CitaCreate(BaseModel):
    nombre: str
    apellido: str
    telefono: str
    correo: EmailStr
    direccion: str
    domicilio: str  # "si" o "no"
    fecha: date
    hora: str  # formato "HH:MM"
    id_pago: Optional[int] = None
    id_empresa: Optional[int] = None
    numero_ticket: Optional[str] = None
    productos: Optional[List[int]] = []  # lista de IDs de productos

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
    productos: List[ProductoBase] = []  # puedes retornar detalles de productos

class PagoSchema(BaseModel):
    id_pago: int
    metodo: str
    valor: float

    class Config:
        orm_mode = True

class EmpresaSchema(BaseModel):
    id_empresa: int
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        orm_mode = True

class ProductoSchema(BaseModel):
    id_producto: int
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

    class Config:
        orm_mode = True

# para devolver empresas con sus productos
class EmpresaWithProductos(EmpresaSchema):
    productos: List[ProductoSchema] = []

    class Config:
        orm_mode = True