from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List
from app.database import get_db
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioCreate, UsuarioOut
import shutil, uuid, os
from pydantic import EmailStr

# Asegura que exista la carpeta donde se guardan las imágenes
os.makedirs("app/static/images", exist_ok=True)

# Declaración del router
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Motor de plantillas HTML
templates = Jinja2Templates(directory="app/templates")


# ============================================================
#                     RUTAS HTML (INTERFAZ WEB)
# ============================================================

# Pantalla principal de usuarios
@router.get("/opciones", response_class=HTMLResponse)
async def opciones_usuarios(request: Request):
    return templates.TemplateResponse("usuarios/opciones.html", {"request": request})


# Formulario para crear usuario
@router.get("/crear_form", response_class=HTMLResponse)
async def crear_usuario_form(request: Request):
    return templates.TemplateResponse("usuarios/crear_usuario.html", {"request": request})


# Listado de usuarios activos
@router.get("/listar_form", response_class=HTMLResponse)
async def listar_usuarios_html(request: Request, db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).filter(Usuario.estado == "activo").all()
    return templates.TemplateResponse("usuarios/listar_usuarios.html", {
        "request": request,
        "usuarios": usuarios
    })


# Listado de usuarios inactivos
@router.get("/inactivos_form", response_class=HTMLResponse)
async def listar_inactivos_html(request: Request, db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).filter(Usuario.estado == "inactivo").all()
    return templates.TemplateResponse("usuarios/listar_usuarios_inactivos.html", {
        "request": request,
        "usuarios": usuarios
    })


# Formulario para buscar usuario por ID
@router.get("/buscar_form", response_class=HTMLResponse)
async def buscar_usuario_form(request: Request):
    return templates.TemplateResponse("usuarios/buscar_usuario.html", {"request": request})


# Formulario para ingresar ID antes de actualizar
@router.get("/actualizar_form", response_class=HTMLResponse)
async def actualizar_usuario_form_id(request: Request):
    return templates.TemplateResponse("usuarios/actualizar_usuario_id.html", {"request": request})


# Formulario para eliminar usuario
@router.get("/eliminar_form", response_class=HTMLResponse)
async def eliminar_usuario_form(request: Request):
    return templates.TemplateResponse("usuarios/eliminar_usuario.html", {"request": request})


# ============================================================
#                     RUTAS POST (FORMULARIOS HTML)
# ============================================================

# Crear usuario desde formulario HTML
@router.post("/crear_form", response_class=HTMLResponse)
async def crear_usuario_html(
    request: Request,
    nombre: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    ciudad: str = Form(...),
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Verifica que el correo no esté repetido
        existente = db.query(Usuario).filter(Usuario.correo == correo).first()
        if existente:
            return templates.TemplateResponse("usuarios/crear_usuario.html", {
                "request": request,
                "error": "El correo ya está registrado"
            })
        
        # Guarda la imagen
        extension = imagen.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{extension}"
        file_location = f"app/static/images/{filename}"
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        
        # Crea el usuario nuevo
        nuevo = Usuario(
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            ciudad=ciudad,
            imagen=filename,
            estado="activo"
        )
        
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        
        return templates.TemplateResponse("usuarios/crear_usuario.html", {
            "request": request,
            "mensaje": f"Usuario '{nombre}' creado exitosamente!"
        })
        
    except Exception as e:
        return templates.TemplateResponse("usuarios/crear_usuario.html", {
            "request": request,
            "error": f"Error al crear usuario: {str(e)}"
        })


# Buscar usuario por ID
@router.post("/buscar_form", response_class=HTMLResponse)
async def buscar_usuario_html(
    request: Request,
    id: int = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    return templates.TemplateResponse("usuarios/buscar_usuario.html", {
        "request": request,
        "usuario": usuario,
        "mensaje": "Usuario no encontrado" if not usuario else None
    })


# Muestra datos actuales antes de actualizar
@router.post("/actualizar_form", response_class=HTMLResponse)
async def mostrar_usuario_actualizar(
    request: Request,
    id: int = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        return templates.TemplateResponse("usuarios/actualizar_usuario_id.html", {
            "request": request,
            "error": f"No se encontró usuario con ID {id}"
        })
    
    return templates.TemplateResponse("usuarios/actualizar_usuario.html", {
        "request": request,
        "usuario": usuario
    })


# Actualiza datos del usuario desde formulario
@router.post("/actualizar_form_post", response_class=HTMLResponse)
async def actualizar_usuario_html(
    request: Request,
    id: int = Form(...),
    nombre: str = Form(None),
    correo: str = Form(None),
    telefono: str = Form(None),
    ciudad: str = Form(None),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    
    if not usuario:
        return templates.TemplateResponse("usuarios/actualizar_usuario_id.html", {
            "request": request,
            "error": f"No se encontró usuario con ID {id}"
        })
    
    # Actualiza campos si fueron enviados
    if nombre:
        usuario.nombre = nombre
    if correo:
        # Valida que el nuevo correo no sea de otro usuario
        otro_usuario = db.query(Usuario).filter(
            Usuario.correo == correo, 
            Usuario.id != id
        ).first()
        if otro_usuario:
            return templates.TemplateResponse("usuarios/actualizar_usuario.html", {
                "request": request,
                "usuario": usuario,
                "error": "El correo ya está registrado por otro usuario"
            })
        usuario.correo = correo
    if telefono:
        usuario.telefono = telefono
    if ciudad:
        usuario.ciudad = ciudad
    
    # Reemplaza la imagen si se envió una nueva
    if imagen and imagen.filename:
        extension = imagen.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{extension}"
        file_location = f"app/static/images/{filename}"
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        usuario.imagen = filename
    
    db.commit()
    db.refresh(usuario)
    
    return templates.TemplateResponse("usuarios/actualizar_usuario.html", {
        "request": request,
        "usuario": usuario,
        "mensaje": "Usuario actualizado exitosamente!"
    })


# Eliminar usuario con validación de productos activos relacionados
@router.post("/eliminar_form", response_class=HTMLResponse)
async def eliminar_usuario_html(
    request: Request,
    id: int = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    
    if not usuario:
        return templates.TemplateResponse("usuarios/eliminar_usuario.html", {
            "request": request,
            "error": f"No se encontró usuario con ID {id}"
        })
    
    # Solo productos activos impiden la eliminación
    relacionado = db.query(Producto).filter(
        Producto.usuario_id == id,
        Producto.estado == "activo"
    ).first()
    
    if relacionado:
        return templates.TemplateResponse("usuarios/eliminar_usuario.html", {
            "request": request,
            "error": "No se puede eliminar: usuario asociado a productos ACTIVOS."
        })
    
    # Marca el usuario como inactivo
    usuario.estado = "inactivo"
    db.commit()
    
    return templates.TemplateResponse("usuarios/eliminar_usuario.html", {
        "request": request,
        "mensaje": f"Usuario '{usuario.nombre}' eliminado correctamente"
    })


# Reactivar usuario inactivo
@router.post("/reactivar_form", response_class=HTMLResponse)
async def reactivar_usuario_html(
    request: Request,
    id: int = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    
    if not usuario:
        usuarios = db.query(Usuario).filter(Usuario.estado == "inactivo").all()
        return templates.TemplateResponse("usuarios/listar_usuarios_inactivos.html", {
            "request": request,
            "usuarios": usuarios,
            "error": f"No se encontró usuario con ID {id}"
        })
    
    if usuario.estado == "activo":
        usuarios = db.query(Usuario).filter(Usuario.estado == "inactivo").all()
        return templates.TemplateResponse("usuarios/listar_usuarios_inactivos.html", {
            "request": request,
            "usuarios": usuarios,
            "error": "El usuario ya está activo"
        })
    
    usuario.estado = "activo"
    db.commit()
    
    usuarios = db.query(Usuario).filter(Usuario.estado == "inactivo").all()
    return templates.TemplateResponse("usuarios/listar_usuarios_inactivos.html", {
        "request": request,
        "usuarios": usuarios,
        "mensaje": f"Usuario '{usuario.nombre}' reactivado correctamente"
    })


# ============================================================
#                    RUTAS API (JSON)
# ============================================================

# Crear usuario desde la API
@router.post("/api", response_model=UsuarioOut)
async def crear_usuario_api(
    nombre: str = Form(...),
    correo: EmailStr = Form(...),
    telefono: str = Form(...),
    ciudad: str = Form(...),
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Verifica duplicado
    existente = db.query(Usuario).filter(Usuario.correo == correo).first()
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # Guarda la imagen
    extension = imagen.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    file_location = f"app/static/images/{filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(imagen.file, buffer)

    # Crea usuario
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


# Listar usuarios activos API
@router.get("/api", response_model=List[UsuarioOut])
def listar_usuarios_api(db: Session = Depends(get_db)):
    return db.query(Usuario).filter(Usuario.estado == "activo").all()


# Listar usuarios inactivos API
@router.get("/api/inactivos", response_model=List[UsuarioOut])
def listar_usuarios_inactivos_api(db: Session = Depends(get_db)):
    return db.query(Usuario).filter(Usuario.estado == "inactivo").all()


# Obtener usuario por ID
@router.get("/api/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario_api(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# Actualizar usuario API
@router.put("/api/{usuario_id}", response_model=UsuarioOut)
async def actualizar_usuario_api(
    usuario_id: int,
    nombre: str | None = Form(None),
    correo: EmailStr | None = Form(None),
    telefono: str | None = Form(None),
    ciudad: str | None = Form(None),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Reemplazar imagen
    if imagen:
        extension = imagen.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{extension}"
        file_location = f"app/static/images/{filename}"

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        usuario.imagen = filename

    # Reemplazar campos si fueron enviados
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


# Eliminar usuario desde API
@router.delete("/api/{usuario_id}")
def eliminar_usuario_api(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    productos = db.query(Producto).filter(Producto.usuario_id == usuario_id).first()
    if productos:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el usuario porque está asociado a productos."
        )

    usuario.estado = "inactivo"
    db.commit()
    return {"mensaje": "Usuario eliminado correctamente"}


# Reactivar usuario desde API
@router.put("/api/reactivar/{usuario_id}", response_model=UsuarioOut)
def reactivar_usuario_api(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.estado == "activo":
        raise HTTPException(status_code=400, detail="El usuario ya está activo")

    usuario.estado = "activo"
    db.commit()
    db.refresh(usuario)
    return usuario


# Subir imagen desde API
@router.post("/api/{usuario_id}/imagen", response_model=UsuarioOut)
def subir_imagen_usuario_api(usuario_id: int, archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    # Verificar que el archivo sea una imagen
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
