from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
    nueva = Categoria(**categoria.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

# Listar todas las categorías
@router.get("/", response_model=list[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).filter(Categoria.estado == "activo").all()

# inactivos
@router.get("/inactivos", response_model=list[CategoriaOut])
def listar_productos_inactivos(db: Session = Depends(get_db)):
    return db.query(Categoria).filter(Categoria.estado == "inactivo").all()


# Buscar categoría por ID
@router.get("/{id}", response_model=CategoriaOut)
def obtener_categoria(id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

# Eliminar categoría
@router.delete("/{id}")
def eliminar_categoria(id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    categoria.estado = "inactivo"
    db.commit()
    return {"mensaje": "Categoría eliminada correctamente"}

# Reactivar categoría inactiva
@router.put("/reactivar/{id}", response_model=CategoriaOut)
def reactivar_categoria(id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == id).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if categoria.estado == "activo":
        raise HTTPException(status_code=400, detail="La categoría ya está activa")

    categoria.estado = "activo"
    db.commit()
    db.refresh(categoria)

    return categoria