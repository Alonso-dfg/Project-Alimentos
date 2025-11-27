from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db
from app.models.proveedor import Proveedor
from app.schemas.proveedor_schema import ProveedorCreate, ProveedorOut
from typing import List

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

# Crear proveedor
@router.post("/", response_model=ProveedorOut)
def crear_proveedor(proveedor: ProveedorCreate, db: Session = Depends(get_db)):
    try:
        nuevo = Proveedor(**proveedor.dict())
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear proveedor")

# Listar proveedores activos
@router.get("/", response_model=List[ProveedorOut])
def listar_proveedores(db: Session = Depends(get_db)):
    try:
        return db.query(Proveedor).filter(Proveedor.estado == "activo").all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al listar proveedores")

# Listar proveedores inactivos
@router.get("/inactivos", response_model=list[ProveedorOut])
def listar_proveedores_inactivos(db: Session = Depends(get_db)):
    try:
        return db.query(Proveedor).filter(Proveedor.estado == "inactivo").all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al listar proveedores inactivos")

# Obtener proveedor por ID
@router.get("/{proveedor_id}", response_model=ProveedorOut)
def obtener_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    try:
        proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        return proveedor
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al obtener proveedor")

# Actualizar proveedor
@router.put("/{proveedor_id}", response_model=ProveedorOut)
def actualizar_proveedor(proveedor_id: int, proveedor_actualizado: ProveedorCreate, db: Session = Depends(get_db)):
    try:
        proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

        for key, value in proveedor_actualizado.dict().items():
            setattr(proveedor, key, value)

        db.commit()
        db.refresh(proveedor)
        return proveedor
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar proveedor")

# Eliminar (inactivar) proveedor
@router.delete("/{proveedor_id}")
def eliminar_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    try:
        proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

        proveedor.estado = "inactivo"
        db.commit()
        return {"mensaje": "Proveedor eliminado correctamente"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar proveedor")
    

# Reactivar proveedor (cambiar estado a activo)
@router.put("/reactivar/{proveedor_id}", response_model=ProveedorOut)
def reactivar_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()

    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    if proveedor.estado == "activo":
        raise HTTPException(status_code=400, detail="El proveedor ya está activo")

    proveedor.estado = "activo"
    db.commit()
    db.refresh(proveedor)

    return proveedor
