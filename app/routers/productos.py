from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import SessionLocal
from app.models.producto import Producto 
from app.models.proveedor import Proveedor
from app.models.categoria import Categoria
from app.models.usuario import Usuario
from app.schemas.producto_schema import ProductoCreate, ProductoUpdate, ProductoOut
import shutil, uuid, os
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/productos", tags=["Productos"])

templates = Jinja2Templates(directory="app/templates")
os.makedirs("app/static/images", exist_ok=True)

# Dependencia para obtener la conexión a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Página con las opciones principales del módulo de productos
@router.get("/opciones", response_class=HTMLResponse)
async def opciones_productos(request: Request):
    return templates.TemplateResponse("productos/productos.html", {"request": request})


# Página con el formulario para crear un producto
@router.get("/crear_form", response_class=HTMLResponse)
async def crear_form(request: Request):
    return templates.TemplateResponse("productos/crear_producto.html", {"request": request})


# Procesa el formulario de creación de producto
@router.post("/crear_form", response_class=HTMLResponse)
async def crear_producto_form(
    request: Request,
    nombre: str = Form(...),
    precio: float = Form(...),
    cantidad: int = Form(...),
    ciudad: str = Form(...),
    categoria_id: int = Form(...),
    proveedor_id: int = Form(...),
    usuario_id: Optional[str] = Form(None),
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validar que la categoría exista y esté activa
    categoria = db.query(Categoria).filter(
        Categoria.id == categoria_id,
        Categoria.estado == "activo"
    ).first()
    
    if not categoria:
        return templates.TemplateResponse("productos/crear_producto.html", {
            "request": request,
            "mensaje_error": f"La categoría ID {categoria_id} no existe o está inactiva"
        })
    
    # Validar que el proveedor exista y esté activo
    proveedor = db.query(Proveedor).filter(
        Proveedor.id == proveedor_id,
        Proveedor.estado == "activo"
    ).first()
    
    if not proveedor:
        return templates.TemplateResponse("productos/crear_producto.html", {
            "request": request,
            "mensaje_error": f"El proveedor ID {proveedor_id} no existe o está inactivo"
        })
    
    # Manejar el usuario asociado. Si no se envía o no existe, se usa 1
    usuario_id_final = 1  
    if usuario_id and usuario_id.strip():
        try:
            usuario_id_final = int(usuario_id)
            usuario = db.query(Usuario).filter(
                Usuario.id == usuario_id_final,
                Usuario.estado == "activo"
            ).first()
            if not usuario:
                usuario_id_final = 1
        except ValueError:
            usuario_id_final = 1
    
    # Guardar la imagen con un nombre único
    filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
    file_location = f"app/static/images/{filename}"
    
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
    except Exception as e:
        return templates.TemplateResponse("productos/crear_producto.html", {
            "request": request,
            "mensaje_error": f"Error al guardar la imagen: {str(e)}"
        })
    
    # Crear el producto en BD
    try:
        nuevo = Producto(
            nombre=nombre,
            precio=precio,
            cantidad=cantidad,
            ciudad=ciudad,
            categoria_id=categoria_id,
            proveedor_id=proveedor_id,
            usuario_id=usuario_id_final,
            imagen=filename
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        
        return templates.TemplateResponse("productos/crear_producto.html", {
            "request": request,
            "mensaje_exito": f"Producto '{nombre}' creado correctamente."
        })
        
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse("productos/crear_producto.html", {
            "request": request,
            "mensaje_error": f"Error al crear producto: {str(e)}"
        })


# Formulario para buscar un producto
@router.get("/buscar_form", response_class=HTMLResponse)
async def buscar_form(request: Request):
    return templates.TemplateResponse("productos/buscar_producto.html", {"request": request})


# Busca un producto por ID y lo muestra
@router.post("/buscar_form", response_class=HTMLResponse)
async def buscar_producto_form(request: Request, id: int = Form(...), db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        mensaje = f"No se encontró ningún producto con ID {id}"
        return templates.TemplateResponse("productos/buscar_producto.html", {"request": request, "mensaje": mensaje})
    return templates.TemplateResponse("productos/buscar_producto.html", {"request": request, "producto": producto})


# Muestra formulario para ingresar el ID del producto a actualizar
@router.get("/actualizar_form", response_class=HTMLResponse)
async def actualizar_form_id(request: Request):
    return templates.TemplateResponse("productos/actualizar_producto_id.html", {"request": request})


# Carga los datos actuales del producto para editarlos
@router.post("/actualizar_form", response_class=HTMLResponse)
async def actualizar_producto_form(request: Request, id: int = Form(...), db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        mensaje = f"No se encontró ningún producto con ID {id}"
        return templates.TemplateResponse("productos/actualizar_producto_id.html", {"request": request, "mensaje": mensaje})
    return templates.TemplateResponse("productos/actualizar_producto.html", {"request": request, "producto": producto})


# Procesa la actualización del producto
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

    # Actualiza cada campo solo si se envía uno nuevo
    if nombre: producto.nombre = nombre
    if precio is not None: producto.precio = precio
    if cantidad is not None: producto.cantidad = cantidad
    if ciudad: producto.ciudad = ciudad
    if categoria_id is not None: producto.categoria_id = categoria_id
    if proveedor_id is not None: producto.proveedor_id = proveedor_id
    if usuario_id is not None: producto.usuario_id = usuario_id

    # Si se manda una nueva imagen, se guarda y reemplaza la anterior
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        file_location = f"app/static/images/{filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        producto.imagen = filename

    db.commit()
    db.refresh(producto)

    mensaje = f"Producto ID {id} actualizado correctamente."
    return templates.TemplateResponse("productos/actualizar_producto.html", {"request": request, "producto": producto, "mensaje": mensaje})


# Lista todos los productos activos en la interfaz HTML
@router.get("/listar_todos", response_class=HTMLResponse)
async def listar_productos_html(request: Request, db: Session = Depends(get_db)):
    productos = db.query(Producto).filter(Producto.estado == "activo").all()
    return templates.TemplateResponse("productos/listar_productos.html", {"request": request, "productos": productos})


# Formulario para eliminar un producto
@router.get("/eliminar_form", response_class=HTMLResponse)
async def eliminar_producto_form(request: Request):
    return templates.TemplateResponse("productos/eliminar_producto.html", {"request": request})


# Procesa la eliminación de un producto desde HTML
@router.post("/eliminar_form", response_class=HTMLResponse)
async def eliminar_producto_post(
    request: Request, 
    id: int = Form(...), 
    db: Session = Depends(get_db)
):
    producto = db.query(Producto).filter(Producto.id == id).first()

    if not producto:
        return templates.TemplateResponse("productos/eliminar_producto.html", {
            "request": request,
            "mensaje": "Producto no encontrado"
        })
    
    # No se permite eliminar si aún tiene stock
    if producto.cantidad > 0:
        return templates.TemplateResponse("productos/eliminar_producto.html", {
            "request": request,
            "mensaje": f"No se puede eliminar. Tiene {producto.cantidad} unidades en stock."
        })
    
    # Si ya está inactivo, no hacer nada
    if producto.estado == "inactivo":
        return templates.TemplateResponse("productos/eliminar_producto.html", {
            "request": request,
            "mensaje": "Este producto ya está eliminado."
        })

    # Se marca como inactivo en BD
    producto.estado = "inactivo"
    db.commit()

    return RedirectResponse("/productos/listar_todos", status_code=303)


# Lista de productos inactivos
@router.get("/inactivos_form", response_class=HTMLResponse)
async def listar_inactivos_html(request: Request, db: Session = Depends(get_db)):
    productos = db.query(Producto).filter(Producto.estado == "inactivo").all()
    return templates.TemplateResponse("productos/listar_productos_inactivos.html", {"request": request, "productos": productos})


# Reactivar un producto que estaba inactivo
@router.post("/reactivar_form", response_class=HTMLResponse)
async def reactivar_producto(request: Request, id: int = Form(...), db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        mensaje = f"No se encontró ningún producto con ID {id}"
        productos = db.query(Producto).filter(Producto.estado == "inactivo").all()
        return templates.TemplateResponse("productos/listar_productos_inactivos.html", {"request": request, "productos": productos, "mensaje": mensaje})

    producto.estado = "activo"
    db.commit()
    mensaje = f"Producto ID {id} reactivado correctamente."
    productos = db.query(Producto).filter(Producto.estado == "inactivo").all()
    return templates.TemplateResponse("productos/listar_productos_inactivos.html", {"request": request, "productos": productos, "mensaje": mensaje})


# ----------------------------- API -----------------------------


# Búsqueda de productos desde la API mediante filtros
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


# API: lista los productos activos
@router.get("/", response_model=List[ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(Producto).filter(Producto.estado == "activo").all()


# API: lista los productos inactivos
@router.get("/inactivos", response_model=List[ProductoOut])
def listar_productos_inactivos(db: Session = Depends(get_db)):
    return db.query(Producto).filter(Producto.estado == "inactivo").all()


# API: creación de producto con envío de imagen
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


# API: actualización completa o parcial del producto
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

    # Actualizar solo los campos enviados
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

    # Si llega una imagen nueva, reemplaza la existente
    if imagen:
        filename = f"{uuid.uuid4()}.{imagen.filename.split('.')[-1]}"
        file_location = f"app/static/images/{filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        producto.imagen = filename

    db.commit()
    db.refresh(producto)

    return producto


# API: eliminar producto aplicando validaciones
@router.delete("/{id}")
def eliminar_producto_api(id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # No se permite eliminar si tiene existencia en inventario
    if producto.cantidad > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar el producto. Tiene {producto.cantidad} unidades en stock."
        )
    
    # Si ya está inactivo, no eliminar dos veces
    if producto.estado == "inactivo":
        raise HTTPException(
            status_code=400, 
            detail="El producto ya está eliminado."
        )
    
    producto.estado = "inactivo"
    db.commit()
    
    return {
        "mensaje": "Producto eliminado correctamente",
        "id": producto.id,
        "nombre": producto.nombre
    }


# API: obtener producto por ID
@router.get("/{id}", response_model=ProductoOut)
def obtener_producto(id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto
