from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.producto import Producto  
from app.schemas.producto_schema import ProductoCreate, ProductoUpdate, ProductoOut
import shutil, uuid, os
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/productos", tags=["Productos"])

templates = Jinja2Templates(directory="app/templates")
os.makedirs("app/static/images", exist_ok=True)

# -----------------------------
# Dependencia DB
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# HTML: opciones de productos
# -----------------------------
@router.get("/opciones", response_class=HTMLResponse)
async def opciones_productos(request: Request):
    return templates.TemplateResponse("productos/productos.html", {"request": request})

# -----------------------------
# HTML: formulario crear producto
# -----------------------------
@router.get("/crear_form", response_class=HTMLResponse)
async def crear_form(request: Request):
    return templates.TemplateResponse("productos/crear_producto.html", {"request": request})

# -----------------------------
# HTML: formulario crear producto (POST) con mensaje
# -----------------------------
@router.post("/crear_form", response_class=HTMLResponse)
async def crear_producto_form(
    request: Request,
    nombre: str = Form(...),
    precio: float = Form(...),
    cantidad: int = Form(...),
    ciudad: str = Form(...),
    categoria_id: int = Form(...),
    proveedor_id: int = Form(...),
    usuario_id: int = Form(...),
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Guardar imagen
    filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
    file_location = f"app/static/images/{filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(imagen.file, buffer)

    # Crear producto en DB
    nuevo = Producto(
        nombre=nombre,
        precio=precio,
        cantidad=cantidad,
        ciudad=ciudad,
        categoria_id=categoria_id,
        proveedor_id=proveedor_id,
        usuario_id=usuario_id,
        imagen=filename
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    # Renderizar el mismo formulario con mensaje de éxito
    return templates.TemplateResponse("productos/crear_producto.html", {
        "request": request,
        "mensaje": f"Producto '{nombre}' creado exitosamente!"
    })


# -----------------------------
# HTML: formulario buscar producto
# -----------------------------
@router.get("/buscar_form", response_class=HTMLResponse)
async def buscar_form(request: Request):
    return templates.TemplateResponse("productos/buscar_producto.html", {"request": request})

#-----------------------------
# HTML: buscar producto por ID y mostrarlo
#-----------------------------
@router.post("/buscar_form", response_class=HTMLResponse)
async def buscar_producto_form(request: Request, id: int = Form(...), db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        mensaje = f"No se encontró ningún producto con ID {id}"
        return templates.TemplateResponse("productos/buscar_producto.html", {"request": request, "mensaje": mensaje})
    return templates.TemplateResponse("productos/buscar_producto.html", {"request": request, "producto": producto})

#-----------------------------
# HTML: formulario para ingresar ID a actualizar
#-----------------------------
@router.get("/actualizar_form", response_class=HTMLResponse)
async def actualizar_form_id(request: Request):
    return templates.TemplateResponse("productos/actualizar_producto_id.html", {"request": request})

#-----------------------------
# HTML: recibir ID y mostrar formulario con los datos actuales
#-----------------------------
@router.post("/actualizar_form", response_class=HTMLResponse)
async def actualizar_producto_form(request: Request, id: int = Form(...), db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        mensaje = f"No se encontró ningún producto con ID {id}"
        return templates.TemplateResponse("productos/actualizar_producto_id.html", {"request": request, "mensaje": mensaje})
    return templates.TemplateResponse("productos/actualizar_producto.html", {"request": request, "producto": producto})

#-----------------------------
# HTML: recibir datos actualizados y procesar actualización
#-----------------------------
@router.post("/actualizar_form_post", response_class=HTMLResponse)
async def actualizar_producto_post(
    request: Request,
    id: int = Form(...),
    nombre: str | None = Form(None),
    precio: float | None = Form(None),
    cantidad: int | None = Form(None),
    ciudad: str | None = Form(None),
    categoria_id: int | None = Form(None),
    proveedor_id: int | None = Form(None),
    usuario_id: int | None = Form(None),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        mensaje = f"No se encontró ningún producto con ID {id}"
        return templates.TemplateResponse("productos/actualizar_producto_id.html", {"request": request, "mensaje": mensaje})

    # Actualizar campos solo si se envían
    if nombre: producto.nombre = nombre
    if precio is not None: producto.precio = precio
    if cantidad is not None: producto.cantidad = cantidad
    if ciudad: producto.ciudad = ciudad
    if categoria_id is not None: producto.categoria_id = categoria_id
    if proveedor_id is not None: producto.proveedor_id = proveedor_id
    if usuario_id is not None: producto.usuario_id = usuario_id

    # Actualizar imagen si se envía
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        file_location = f"app/static/images/{filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        producto.imagen = filename

    db.commit()
    db.refresh(producto)

    mensaje = f"Producto ID {id} actualizado exitosamente!"
    return templates.TemplateResponse("productos/actualizar_producto.html", {"request": request, "producto": producto, "mensaje": mensaje})


#-----------------------------
# HTML: listar todos los productos activos
#-----------------------------
@router.get("/listar_todos", response_class=HTMLResponse)
async def listar_productos_html(request: Request, db: Session = Depends(get_db)):
    productos = db.query(Producto).filter(Producto.estado == "activo").all()
    return templates.TemplateResponse("productos/listar_productos.html", {"request": request, "productos": productos})

# -----------------------------
# HTML: formulario para eliminar producto
# -----------------------------
@router.get("/eliminar_form", response_class=HTMLResponse)
async def eliminar_form(request: Request):
    return templates.TemplateResponse("productos/eliminar_producto.html", {"request": request})


# -----------------------------
# HTML: eliminar producto
# -----------------------------
@router.post("/eliminar_form", response_class=HTMLResponse)
async def eliminar_producto_form(request: Request, id: int = Form(...), db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        mensaje = f"No se encontró ningún producto con ID {id}"
        return templates.TemplateResponse("productos/eliminar_producto.html", {"request": request, "mensaje": mensaje})

    producto.estado = "inactivo"
    db.commit()
    mensaje = f"Producto ID {id} eliminado correctamente!"
    return templates.TemplateResponse("productos/eliminar_producto.html", {"request": request, "mensaje": mensaje})

# HTML: listar productos inactivos
@router.get("/inactivos_form", response_class=HTMLResponse)
async def listar_inactivos_html(request: Request, db: Session = Depends(get_db)):
    productos = db.query(Producto).filter(Producto.estado == "inactivo").all()
    return templates.TemplateResponse("productos/listar_productos_inactivos.html", {"request": request, "productos": productos})

# HTML: reactivar producto
@router.post("/reactivar_form", response_class=HTMLResponse)
async def reactivar_producto(request: Request, id: int = Form(...), db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        mensaje = f"No se encontró ningún producto con ID {id}"
        productos = db.query(Producto).filter(Producto.estado == "inactivo").all()
        return templates.TemplateResponse("productos/listar_productos_inactivos.html", {"request": request, "productos": productos, "mensaje": mensaje})

    producto.estado = "activo"
    db.commit()
    mensaje = f"Producto ID {id} reactivado correctamente!"
    productos = db.query(Producto).filter(Producto.estado == "inactivo").all()
    return templates.TemplateResponse("productos/listar_productos_inactivos.html", {"request": request, "productos": productos, "mensaje": mensaje})













# -----------------------------
# API: buscar productos
# -----------------------------
@router.get("/buscar")
def buscar_productos(
    nombre: str | None = Query(None),
    ciudad: str | None = Query(None),
    categoria_id: int | None = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Producto)
    if nombre:
        query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))  
    if ciudad:
        query = query.filter(Producto.ciudad.ilike(f"%{ciudad}%"))
    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)
    productos = query.all()
    if not productos:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return {"cantidad": len(productos), "productos": productos}

# -----------------------------
# API: listar todos los productos activos
# -----------------------------
@router.get("/", response_model=list[ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(Producto).filter(Producto.estado == "activo").all()

# -----------------------------
# API: listar productos inactivos
# -----------------------------
@router.get("/inactivos", response_model=list[ProductoOut])
def listar_productos_inactivos(db: Session = Depends(get_db)):
    return db.query(Producto).filter(Producto.estado == "inactivo").all()

# -----------------------------
# API: crear producto
# -----------------------------
@router.post("/", response_model=ProductoOut)
async def crear_producto(
    nombre: str = Form(...),
    precio: float = Form(...),
    cantidad: int = Form(...),
    ciudad: str = Form(...),
    categoria_id: int = Form(...),
    proveedor_id: int = Form(...),
    usuario_id: int = Form(...),
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
    file_location = f"app/static/images/{filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(imagen.file, buffer)

    nuevo = Producto(
        nombre=nombre,
        precio=precio,
        cantidad=cantidad,
        ciudad=ciudad,
        categoria_id=categoria_id,
        proveedor_id=proveedor_id,
        usuario_id=usuario_id,
        imagen=filename
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# -----------------------------
# API: actualizar producto
# -----------------------------
@router.put("/{id}", response_model=ProductoOut)
async def actualizar_producto(
    id: int,
    nombre: str | None = Form(None),
    precio: float | None = Form(None),
    cantidad: int | None = Form(None),
    ciudad: str | None = Form(None),
    categoria_id: int | None = Form(None),
    proveedor_id: int | None = Form(None),
    usuario_id: int | None = Form(None),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if nombre is not None:
        producto.nombre = nombre
    if precio is not None:
        producto.precio = precio
    if cantidad is not None:
        producto.cantidad = cantidad
    if ciudad is not None:
        producto.ciudad = ciudad
    if categoria_id is not None:
        producto.categoria_id = categoria_id
    if proveedor_id is not None:
        producto.proveedor_id = proveedor_id
    if usuario_id is not None:
        producto.usuario_id = usuario_id
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        file_location = f"app/static/images/{filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        producto.imagen = filename

    db.commit()
    db.refresh(producto)
    return producto

# -----------------------------
# API: eliminar producto (inactivo)
# -----------------------------
@router.delete("/{id}")
def eliminar_producto(id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto.estado = "inactivo"
    db.commit()
    return {"mensaje": "Producto eliminado correctamente"}

# -----------------------------
# API: obtener producto por ID
# -----------------------------
@router.get("/{id}", response_model=ProductoOut)
def obtener_producto(id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto
