from sqlalchemy import Column, Integer, String, Boolean, Date, Time, Table, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

# Tabla intermedia para relación muchos a muchos
cita_productos = Table(
    "cita_productos",
    Base.metadata,
    Column("id_cita", Integer, ForeignKey("citas.id"), primary_key=True),
    Column("id_producto", Integer, ForeignKey("productos.id_producto"), primary_key=True)
)

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

    empresas = relationship(
        "Empresa",
        secondary=empresa_productos,
        back_populates="productos"
    )

    citas = relationship("Cita", secondary=cita_productos, back_populates="productos")


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

    productos = relationship("Producto", secondary=cita_productos, back_populates="citas")

    numero_ticket = Column(String(50), nullable=True)
    cantidad_productos = Column(Integer, nullable=True)
