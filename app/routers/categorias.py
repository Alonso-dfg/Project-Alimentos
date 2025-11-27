from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal
from app.models.categoria import Categoria
from app.schemas.categoria_schema import CategoriaCreate, CategoriaOut

router = APIRouter(prefix="/categorias", tags=["Categorías"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear categoría
@router.post("/", response_model=CategoriaOut)
def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    try:
        nueva = Categoria(**categoria.dict())
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        return nueva
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear categoría")

# Listar categorías activas
@router.get("/", response_model=list[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    try:
        return db.query(Categoria).filter(Categoria.estado == "activo").all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al listar categorías")

# Listar categorías inactivas
@router.get("/inactivos", response_model=list[CategoriaOut])
def listar_categorias_inactivas(db: Session = Depends(get_db)):
    try:
        return db.query(Categoria).filter(Categoria.estado == "inactivo").all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al listar categorías inactivas")

# Obtener categoría por ID
@router.get("/{id}", response_model=CategoriaOut)
def obtener_categoria(id: int, db: Session = Depends(get_db)):
    try:
        categoria = db.query(Categoria).filter(Categoria.id == id).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return categoria
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al obtener categoría")

# Eliminar (inactivar) categoría
@router.delete("/{id}")
def eliminar_categoria(id: int, db: Session = Depends(get_db)):
    try:
        categoria = db.query(Categoria).filter(Categoria.id == id).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        categoria.estado = "inactivo"
        db.commit()
        return {"mensaje": "Categoría eliminada correctamente"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar categoría")
    
# Reactivar categoría (volver a estado activo)
@router.put("/reactivar/{id}", response_model=CategoriaOut)
def reactivar_categoria(id: int, db: Session = Depends(get_db)):
    try:
        categoria = db.query(Categoria).filter(Categoria.id == id).first()

        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        if categoria.estado == "activo":
            raise HTTPException(status_code=400, detail="La categoría ya está activa")

        categoria.estado = "activo"
        db.commit()
        db.refresh(categoria)
        return categoria

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al reactivar la categoría")

