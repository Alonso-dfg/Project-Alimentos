from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models.producto import Producto
from app.schemas.producto_schema import ProductoCreate, ProductoUpdate
from app.database import get_db
from sqlalchemy.exc import SQLAlchemyError
import traceback 




router = APIRouter(prefix="/productos", tags=["Productos"])


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

    except Exception as e:
        db.rollback()
        print("\n=== ERROR REAL ===")
        traceback.print_exc()     # ← imprime el traceback completo
        print("==================\n")
        raise e

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


#POST: Crear un producto
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_producto(data: ProductoCreate, db: Session = Depends(get_db)):
    try:
        nuevo_producto = Producto(**data.dict())

        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)

        return nuevo_producto

    except Exception as e:
        db.rollback()
        print("\n=== ERROR REAL ===")
        traceback.print_exc()     # ← imprime el traceback completo
        print("==================\n")
        raise e

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