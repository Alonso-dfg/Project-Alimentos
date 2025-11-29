from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioCreate, UsuarioOut
import shutil, uuid, os
from pydantic import EmailStr

os.makedirs("app/static/images", exist_ok=True)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

""""
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
"""
# CREAR USUARIO CON IMAGEN
@router.post("/", response_model=UsuarioOut)
async def crear_usuario(
    nombre: str = Form(...),
    correo: EmailStr = Form(...),
    telefono: str = Form(...),
    ciudad: str = Form(...),
    imagen: UploadFile = File(...),  # 🔥 obligatorio
    db: Session = Depends(get_db)
):

    existente = db.query(Usuario).filter(Usuario.correo == correo).first()
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # Guardar imagen
    extension = imagen.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    file_location = f"app/static/images/{filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(imagen.file, buffer)

    nuevo = Usuario(
        nombre=nombre,
        correo=correo,
        telefono=telefono,
        ciudad=ciudad,
        imagen=filename
    )

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
"""
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
"""
# ACTUALIZAR USUARIO CON IMAGEN
@router.put("/{usuario_id}", response_model=UsuarioOut)
async def actualizar_usuario(
    usuario_id: int,
    nombre: str | None = Form(None),
    correo: EmailStr | None = Form(None),
    telefono: str | None = Form(None),
    ciudad: str | None = Form(None),
    imagen: UploadFile | None = File(None),   # 🔥 opcional
    db: Session = Depends(get_db)
):

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Si viene imagen nueva
    if imagen:
        extension = imagen.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{extension}"
        file_location = f"app/static/images/{filename}"

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)

        usuario.imagen = filename

    # Campos opcionales
    if nombre is not None:
        usuario.nombre = nombre
    if correo is not None:
        usuario.correo = correo
    if telefono is not None:
        usuario.telefono = telefono
    if ciudad is not None:
        usuario.ciudad = ciudad

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

# Reactivar usuario inactivo
@router.put("/reactivar/{usuario_id}", response_model=UsuarioOut)
def reactivar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.estado == "activo":
        raise HTTPException(status_code=400, detail="El usuario ya está activo")

    usuario.estado = "activo"
    db.commit()
    db.refresh(usuario)

    return usuario

# Subir imagen para un usuario
@router.post("/{usuario_id}/imagen", response_model=UsuarioOut)
def subir_imagen_usuario(usuario_id: int, archivo: UploadFile = File(...), db: Session = Depends(get_db)):

    if not archivo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    extension = archivo.filename.split(".")[-1]
    nombre_archivo = f"{uuid.uuid4()}.{extension}"
    ruta = f"static/images/{nombre_archivo}"

    with open(ruta, "wb") as buffer:
        shutil.copyfileobj(archivo.file, buffer)

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.imagen = nombre_archivo
    db.commit()
    db.refresh(usuario)

    return usuario
