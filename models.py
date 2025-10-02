from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Time, Float, DECIMAL, Table, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# Tabla intermedia para relación muchos a muchos
class CitaProducto(Base):
    __tablename__ = "cita_productos"
    id_cita = Column(Integer, ForeignKey("citas.id"), primary_key=True)  
    id_producto = Column(Integer, ForeignKey("productos.id_producto"))
    cantidad = Column(Integer)
    precio_unitario = Column(DECIMAL(10, 2), nullable=True)
    # relaciones:
    producto = relationship("Producto", back_populates="cita_productos")
    # FALTA ESTA LINEA:
    cita = relationship("Cita", back_populates="productos")

# Tabla intermedia
empresa_productos = Table(
    "empresa_productos",
    Base.metadata,
    Column("id_empresa", ForeignKey("empresas.id_empresa"), primary_key=True),
    Column("id_producto", ForeignKey("productos.id_producto"), primary_key=True)
)

# Modelo: Empresa
class Empresa(Base):
    __tablename__ = "empresas"
    id_empresa = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    descripcion = Column(String)
    productos = relationship(
        "Producto",
        secondary=empresa_productos,
        back_populates="empresas"
    )
    citas = relationship("Cita", back_populates="empresa")

# Modelo: Pago
class Pago(Base):
    __tablename__ = "pagos"
    id_pago = Column(Integer, primary_key=True, index=True)
    metodo = Column(String(50)) 
    citas = relationship("Cita", back_populates="pago")
 
# Modelo: Producto
class Producto(Base):
    __tablename__ = "productos"
    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    descripcion = Column(String)
    precio = Column(Float)
    cantidad_existente = Column(Integer, nullable=True) 
    empresas = relationship(
        "Empresa",
        secondary=empresa_productos,
        back_populates="productos"
    )
    cita_productos = relationship("CitaProducto", back_populates="producto")

# Modelo: Cita
class Cita(Base):
    __tablename__ = "citas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    apellido = Column(String(100))
    telefono = Column(String(20))
    correo = Column(String(100))  # campo agregado
    direccion = Column(String(255))
    domicilio = Column(Boolean)
    fecha = Column(Date)
    hora = Column(Time)
    # Campos nuevos para domicilio
    distancia_km = Column(Float, nullable=True)        # Distancia estimada para el domicilio
    costo_domicilio = Column(Float, nullable=True)     # Costo calculado para el domicilio
    # Relaciones
    id_pago = Column(Integer, ForeignKey("pagos.id_pago"), nullable=True)
    pago = relationship("Pago")
    id_empresa = Column(Integer, ForeignKey("empresas.id_empresa"), nullable=True)
    empresa = relationship("Empresa", back_populates="citas") 
    numero_ticket = Column(String(50), nullable=True)
    cantidad_productos = Column(Integer, nullable=True)
    # relación con CitaProducto
    cita_productos = relationship("CitaProducto", back_populates="cita")
    # Campos para calculo de valores
    valor_productos = Column(Float, nullable=True)
    total_pagar = Column(Float, nullable=True)
    estado = Column(String(20), nullable=False, default="activa")
    productos = relationship("CitaProducto", back_populates="cita", cascade="all, delete-orphan")

# Manejo de estados
class CitaAnulada(Base):
    __tablename__ = 'citas_anuladas'

    id = Column(Integer, primary_key=True, index=True)
    id_cita = Column(Integer, nullable=False)
    fecha_anulacion = Column(DateTime, default=datetime.utcnow)
    comentario = Column(String)
class CitaModificada(Base):
    __tablename__ = 'citas_modificadas'

    id = Column(Integer, primary_key=True, index=True)
    id_cita = Column(Integer, nullable=False)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow)
    datos_anteriores = Column(String)  # Puedes usar JSON si usas PostgreSQL