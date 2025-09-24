from fastapi import FastAPI, Depends, HTTPException

from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from schemas import CitaCreate, CitaRead
from crud import crear_cita
from models import Cita, Empresa, Producto
from typing import List
from schemas import EmpresaSchema
from schemas import ProductoSchema
# Relación empresas productos
from fastapi import HTTPException

#Agregar CORS 
from fastapi.middleware.cors import CORSMiddleware


# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 👇 configuración de CORS aquí
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

# En allow_origins puedes usar la lista que definiste
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # usar la variable 'origins' que definiste arriba
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/citas", response_model=CitaRead)
def guardar_cita(cita: CitaCreate, db: Session = Depends(get_db)):
    nueva = crear_cita(db, cita)
    return nueva

# Endpoint para productos, empresas y pagos si los necesitas
# Por ejemplo:
@app.post("/productos")
def crear_producto(descripcion: str, db: Session = Depends(get_db)):
    prod = Producto(descripcion=descripcion)
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return {"id_producto": prod.id_producto, "descripcion": prod.descripcion}

@app.post("/empresas")
def crear_empresa(nombre: str, descripcion: str = None, db: Session = Depends(get_db)):
    emp = Empresa(nombre=nombre, descripcion=descripcion)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return {"id_empresa": emp.id_empresa, "nombre": emp.nombre, "descripcion": emp.descripcion}

@app.get("/productos/{id_producto}/empresas", response_model=List[EmpresaSchema])
def obtener_empresas_por_producto(id_producto: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto.empresas

@app.get("/empresas/{id_empresa}/productos", response_model=List[ProductoSchema])
def obtener_productos_por_empresa(id_empresa: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id_empresa == id_empresa).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa.productos





