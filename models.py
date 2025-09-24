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

# empresas.py
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

class Pago(Base):
    __tablename__ = "pagos"
    id_pago = Column(Integer, primary_key=True, index=True)
    metodo = Column(String(50))
    valor = Column(Float)   
    citas = relationship("Cita", back_populates="pago")


# productos.py
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

    citas = relationship("Cita", secondary="cita_productos", back_populates="productos")


class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    apellido = Column(String(100))
    telefono = Column(String(20))
    correo = Column(String(100))  # nuevo
    direccion = Column(String(255))
    domicilio = Column(Boolean)
    fecha = Column(Date)
    hora = Column(Time)

    # Relaciones nuevas
    id_pago = Column(Integer, ForeignKey("pagos.id_pago"), nullable=True)
    pago = relationship("Pago", back_populates="citas")

    id_empresa = Column(Integer, ForeignKey("empresas.id_empresa"), nullable=True)
    empresa = relationship("Empresa", back_populates="citas")

    productos = relationship("Producto", secondary=cita_productos, back_populates="citas")

    numero_ticket = Column(String(50), nullable=True)
    cantidad_productos = Column(Integer, nullable=True)



