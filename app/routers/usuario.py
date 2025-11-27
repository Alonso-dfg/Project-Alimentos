from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=UsuarioOut)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    existente = db.query(Usuario).filter(Usuario.correo == usuario.correo).first()
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    nuevo = Usuario(**usuario.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=List[UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).filter(Usuario.estado == "activo").all()

@router.get("/inactivos", response_model=List[UsuarioOut])
def listar_usuarios_inactivos(db: Session = Depends(get_db)):
    return db.query(Usuario).filter(Usuario.estado == "inactivo").all()

@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(usuario_id: int, datos: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for key, value in datos.dict().items():
        setattr(usuario, key, value)
    db.commit()
    db.refresh(usuario)
    return usuario

@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.estado = "inactivo"
    db.commit()
    return {"mensaje": "Usuario eliminado correctamente"}

# Reactivar usuario (volver a estado activo)
@router.put("/reactivar/{usuario_id}", response_model=UsuarioOut)
def reactivar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    try:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if usuario.estado == "activo":
            raise HTTPException(status_code=400, detail="El usuario ya está activo")

        usuario.estado = "activo"
        db.commit()
        db.refresh(usuario)
        return usuario

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al reactivar el usuario")

