from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from database import SessionLocal, engine, Base
from crud import crear_cita
from models import Cita, Empresa, Pago, Producto
from schemas import (
    CitaCreate,
    CitaRead,
    EmpresaSchema,
    PagoSchema,
    ProductoSchema,
)

#  Crear las tablas automáticamente
Base.metadata.create_all(bind=engine)

# Inicializar app
app = FastAPI()

#  Configuración de CORS para desarrollo local (Angular)
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Dependencia para obtener sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  Guardar una nueva cita
@app.post("/citas", response_model=CitaRead)
def guardar_cita(cita: CitaCreate, db: Session = Depends(get_db)):
    # Validar que el método de pago exista si se proporciona
    if cita.id_pago:
        pago = db.query(Pago).filter(Pago.id_pago == cita.id_pago).first()
        if not pago:
            raise HTTPException(status_code=400, detail="Método de pago no válido")
    
    nueva = crear_cita(db, cita)
    return nueva

#  Crear un producto (modo rápido)
@app.post("/productos")
def crear_producto(descripcion: str, db: Session = Depends(get_db)):
    prod = Producto(descripcion=descripcion)
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return {
        "id_producto": prod.id_producto,
        "descripcion": prod.descripcion,
    }

#  Crear una empresa
@app.post("/empresas")
def crear_empresa(nombre: str, descripcion: str = None, db: Session = Depends(get_db)):
    emp = Empresa(nombre=nombre, descripcion=descripcion)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return {
        "id_empresa": emp.id_empresa,
        "nombre": emp.nombre,
        "descripcion": emp.descripcion,
    }

#  Obtener empresa por ID
@app.get("/empresas/{id_empresa}", response_model=EmpresaSchema)
def obtener_empresa_por_id(id_empresa: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id_empresa == id_empresa).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

#  Obtener empresas relacionadas a un producto
@app.get("/productos/{id_producto}/empresas", response_model=List[EmpresaSchema])
def obtener_empresas_por_producto(id_producto: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto.empresas

#  Obtener productos ofrecidos por una empresa
@app.get("/empresas/{id_empresa}/productos", response_model=List[ProductoSchema])
def obtener_productos_por_empresa(id_empresa: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id_empresa == id_empresa).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa.productos

#  Obtener horas ocupadas en una fecha
@app.get("/citas/ocupadas", response_model=List[str])
def obtener_horas_ocupadas(fecha: date, id_empresa: int = None, db: Session = Depends(get_db)):
    query = db.query(Cita).filter(Cita.fecha == fecha)
    if id_empresa:
        query = query.filter(Cita.id_empresa == id_empresa)
    citas = query.all()
    return [cita.hora.strftime("%H:%M") for cita in citas]

# Obtener todos los métodos de pago disponibles
@app.get("/metodos-pago", response_model=List[PagoSchema])
def obtener_metodos_pago(db: Session = Depends(get_db)):
    return db.query(Pago).all()


