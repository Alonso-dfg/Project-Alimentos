from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from fastapi.responses import FileResponse, HTMLResponse
from app.models.producto import Producto
from app.schemas.producto_schema import ProductoCreate, ProductoUpdate, ProductoOut
from app.database import get_db
from sqlalchemy.exc import SQLAlchemyError
import uuid
import shutil
import os




router = APIRouter(prefix="/productos", tags=["Productos"])



'''''
# GET: Obtener todos los productos
@router.get("/")
def obtener_productos(db: Session = Depends(get_db)):
    try:
        productos = db.query(Producto).all()

        if not productos:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay productos registrados"
            )

        return productos

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener los productos"
        )
'''
@router.get("/productos")
def get_all_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()

    # Convertir la ruta de imagen a URL FastAPI
    response = []
    for p in productos:
        response.append({
            "id": p.id,
            "nombre": p.nombre,
            "precio": p.precio,
            "ciudad": p.ciudad,
            "fuente": p.fuente,
            "categoria_id": p.categoria_id,
            "proveedor_id": p.proveedor_id,
            "usuario_id": p.usuario_id,
            "estado": p.estado,
            "imagen": f"/uploads/{p.imagen}" if p.imagen else None
        })

    return response


# GET: Obtener producto por ID
@router.get("/{producto_id}")
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    try:
        producto = db.query(Producto).filter(Producto.id == producto_id).first()

        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El producto con id {producto_id} no existe"
            )

        return producto

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al buscar el producto"
        )

''''
#POST: Crear un producto
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_producto(data: ProductoCreate, db: Session = Depends(get_db)):
    try:
        nuevo_producto = Producto(**data.dict())

        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)

        return nuevo_producto

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el producto"
        )
'''

# ==========================================================
# POST: Crear producto con imagen opcional
# ==========================================================
@router.post("/productos")
async def crear_producto(
    nombre: str = Form(...),
    precio: float = Form(...),
    ciudad: str = Form(...),
    fuente: str = Form(...),
    categoria_id: int = Form(None),
    proveedor_id: int = Form(None),
    usuario_id: int = Form(None),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    filename = None

    if imagen:
        ext = imagen.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        with open(f"uploads/{filename}", "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)

    nuevo = Producto(
        nombre=nombre,
        precio=precio,
        ciudad=ciudad,
        fuente=fuente,
        categoria_id=categoria_id,
        proveedor_id=proveedor_id,
        usuario_id=usuario_id,
        imagen=filename,
        estado="activo"
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo
    '''
# PUT: Actualizar producto
@router.put("/{producto_id}")
def actualizar_producto(producto_id: int, data: ProductoUpdate, db: Session = Depends(get_db)):
    try:
        producto = db.query(Producto).filter(Producto.id == producto_id).first()

        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El producto con id {producto_id} no existe"
            )

        for key, value in data.dict().items():
            setattr(producto, key, value)

        db.commit()
        db.refresh(producto)

        return producto

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el producto"
        )
        '''
# ==========================================================
# PUT: Actualizar producto
# ==========================================================
@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(
    producto_id: int,
    nombre: str = Form(...),
    precio: float = Form(...),
    ciudad: str = Form(...),
    fuente: str = Form(...),
    categoria_id: int = Form(...),
    proveedor_id: int = Form(...),
    usuario_id: int = Form(...),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        producto = db.query(Producto).filter(Producto.id == producto_id).first()

        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El producto con id {producto_id} no existe"
            )

        # Si se envía nueva imagen la reemplazamos
        if imagen:
            os.makedirs("uploads", exist_ok=True)
            nombre_archivo = imagen.filename
            ruta = f"uploads/{nombre_archivo}"

            with open(ruta, "wb") as f:
                f.write(imagen.file.read())

            producto.imagen = nombre_archivo

        # Actualizar otros campos
        producto.nombre = nombre
        producto.precio = precio
        producto.ciudad = ciudad
        producto.fuente = fuente
        producto.categoria_id = categoria_id
        producto.proveedor_id = proveedor_id
        producto.usuario_id = usuario_id

        db.commit()
        db.refresh(producto)

        return producto

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el producto"
        )
    


# DELETE: Eliminar producto
@router.delete("/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    try:
        producto = db.query(Producto).filter(Producto.id == producto_id).first()

        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El producto con id {producto_id} no existe"
            )

        db.delete(producto)
        db.commit()

        return {"message": "Producto eliminado correctamente"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el producto"
        )