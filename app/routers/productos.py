from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.producto import Producto  
from app.schemas.producto_schema import ProductoCreate, ProductoUpdate, ProductoOut


router = APIRouter(prefix="/productos", tags=["Productos"])

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Busqueda por nombre ciudad y ID categoria
@router.get("/buscar")
def buscar_productos(
    nombre: str | None = Query(None, description="Buscar por nombre del producto"),
    ciudad: str | None = Query(None, description="Buscar por ciudad"),
    categoria_id: int | None = Query(None, description="Buscar por ID de categoría"),
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
        raise HTTPException(status_code=404, detail="No se encontraron productos con esos criterios")

    return {
        "cantidad": len(productos),
        "productos": productos
    }


# Crear producto
@router.post("/", response_model=ProductoOut)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    nuevo = Producto(**producto.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# Listar todos los productos
@router.get("/", response_model=list[ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(Producto).filter(Producto.estado == "activo").all()

# Listar productos inactivos
@router.get("/inactivos", response_model=list[ProductoOut])
def listar_productos_inactivos(db: Session = Depends(get_db)):
    return db.query(Producto).filter(Producto.estado == "inactivo").all()

# Buscar producto por ID
@router.get("/{id}", response_model=ProductoOut)
def obtener_producto(id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# Actualizar producto
@router.put("/{id}", response_model=ProductoOut)
def actualizar_producto(id: int, datos: ProductoUpdate, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in datos.dict().items():
        setattr(producto, key, value)
    db.commit()
    db.refresh(producto)
    return producto

# Eliminar producto
@router.delete("/{id}")
def eliminar_producto(id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto.estado = "inactivo"
    db.commit()
    return {"mensaje": "Producto eliminado correctamente"}

