from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.models.producto import Producto
from app.models.categoria import Categoria
from app.schemas.categoria_schema import CategoriaCreate, CategoriaOut, CategoriaUpdate

# Este router agrupa todas las rutas relacionadas con categorías
router = APIRouter(prefix="/categorias", tags=["Categorías"])

# Carpeta donde están las plantillas HTML
templates = Jinja2Templates(directory="app/templates")

# Función que abre y cierra la conexión a la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===============================
#   VISTAS HTML
# ===============================

# Página principal con las opciones de categorías
@router.get("/opciones", response_class=HTMLResponse)
async def opciones_categorias(request: Request):
    return templates.TemplateResponse("categorias/opciones.html", {"request": request})

# Muestra el formulario para crear una nueva categoría
@router.get("/crear_form", response_class=HTMLResponse)
async def crear_categoria_form(request: Request):
    return templates.TemplateResponse("categorias/crear_categoria.html", {"request": request})

# Recibe el formulario y crea una categoría
@router.post("/crear", response_class=HTMLResponse)
async def crear_categoria_html(request: Request, nombre: str = Form(...)):
    db = SessionLocal()

    nueva = Categoria(nombre=nombre)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    db.close()

    return templates.TemplateResponse(
        "categorias/crear_categoria.html",
        {"request": request, "mensaje": "Categoría creada exitosamente"}
    )

# Lista todas las categorías activas en una página HTML
@router.get("/listar", response_class=HTMLResponse)
async def listar_categorias_html(request: Request):
    db = SessionLocal()
    categorias = db.query(Categoria).filter(Categoria.estado == "activo").all()
    db.close()

    return templates.TemplateResponse(
        "categorias/listar_categorias.html",
        {"request": request, "categorias": categorias}
    )

# Lista categorías inactivas
@router.get("/inactivas", response_class=HTMLResponse)
async def listar_inactivas_html(request: Request):
    db = SessionLocal()
    categorias = db.query(Categoria).filter(Categoria.estado == "inactivo").all()
    db.close()

    return templates.TemplateResponse(
        "categorias/listar_categorias_inactivas.html",
        {"request": request, "categorias": categorias}
    )

# Reactivar categoría desde un formulario
@router.post("/reactivar_form", response_class=HTMLResponse)
async def reactivar_categoria_form(request: Request, id: int = Form(...)):
    db = SessionLocal()
    categoria = db.query(Categoria).filter(Categoria.id == id).first()

    # Si no existe, retorno mensaje
    if not categoria:
        categorias = db.query(Categoria).filter(Categoria.estado == "inactivo").all()
        db.close()
        return templates.TemplateResponse("categorias/listar_categorias_inactivas.html", {
            "request": request,
            "categorias": categorias,
            "mensaje": f"No se encontró categoría con ID {id}"
        })

    # Se activa la categoría
    categoria.estado = "activo"
    db.commit()
    db.refresh(categoria)

    # Se recarga la lista actualizada
    categorias = db.query(Categoria).filter(Categoria.estado == "inactivo").all()
    db.close()

    return templates.TemplateResponse("categorias/listar_categorias_inactivas.html", {
        "request": request,
        "categorias": categorias,
        "mensaje": f"Categoría ID {id} reactivada correctamente!"
    })

# Formulario para buscar categoría por ID
@router.get("/buscar_form", response_class=HTMLResponse)
async def buscar_categoria_form(request: Request):
    return templates.TemplateResponse("categorias/buscar_categoria.html", {"request": request})

# Busca la categoría ingresada por ID
@router.post("/buscar", response_class=HTMLResponse)
async def buscar_categoria_html(request: Request, id: int = Form(...)):
    db = SessionLocal()
    categoria = db.query(Categoria).filter(Categoria.id == id).first()
    db.close()

    return templates.TemplateResponse(
        "categorias/buscar_categoria.html",
        {"request": request, "categoria": categoria}
    )

# ------------------------------
#    ELIMINAR (HTML)
# ------------------------------
@router.get("/eliminar_form", response_class=HTMLResponse)
async def eliminar_categoria_form(request: Request):
    return templates.TemplateResponse("categorias/eliminar_categoria.html", {"request": request})

@router.post("/eliminar_form", response_class=HTMLResponse)
async def eliminar_categoria_post(request: Request, id: int = Form(...), db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == id).first()

    # Si no existe, aviso
    if not categoria:
        return templates.TemplateResponse("categorias/eliminar_categoria.html", {
            "request": request,
            "mensaje": "Categoría no encontrada"
        })

    # Solo se permite eliminar si no tiene productos activos
    productos_activos = db.query(Producto).filter(
        Producto.categoria_id == id,
        Producto.estado == "activo"
    ).first()

    if productos_activos:
        return templates.TemplateResponse("categorias/eliminar_categoria.html", {
            "request": request,
            "mensaje": "No se puede eliminar: categoría asociada a productos ACTIVOS."
        })

    # Se pasa a inactiva
    categoria.estado = "inactivo"
    db.commit()

    return RedirectResponse("/categorias/listar", status_code=303)

# ------------------------------
#    ACTUALIZAR (HTML)
# ------------------------------
@router.get("/actualizar_form")
def actualizar_categoria_form_page(request: Request):
    return templates.TemplateResponse(
        "categorias/actualizar_categoria.html",
        {"request": request}
    )

@router.post("/actualizar_form")
def actualizar_categoria_form(request: Request, id: int = Form(...), nombre: str = Form(...), db: Session = Depends(get_db)):
    try:
        actualizar_categoria(id, CategoriaUpdate(nombre=nombre), db)
        return templates.TemplateResponse(
            "categorias/actualizar_categoria.html",
            {"request": request, "mensaje": "Categoría actualizada correctamente"}
        )
    except HTTPException as e:
        return templates.TemplateResponse(
            "categorias/actualizar_categoria.html",
            {"request": request, "error": e.detail}
        )

# ==================================================
#                API (JSON)
# ==================================================

# Crear categoría (JSON)
@router.post("/", response_model=CategoriaOut)
def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    nueva = Categoria(**categoria.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

# Listar categorías activas
@router.get("/", response_model=List[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).filter(Categoria.estado == "activo").all()

# Listar inactivas
@router.get("/inactivos", response_model=List[CategoriaOut])
def listar_categorias_inactivas(db: Session = Depends(get_db)):
    return db.query(Categoria).filter(Categoria.estado == "inactivo").all()

# Buscar categoría por ID
@router.get("/detalle/{id}", response_model=CategoriaOut)
def obtener_categoria(id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == id).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return categoria

# Eliminar categoría (API)
@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    productos_asociados = db.query(Producto).filter(Producto.categoria_id == categoria_id).first()

    if productos_asociados:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar la categoría porque está asociada a uno o más productos."
        )

    categoria.estado = "inactivo"
    db.commit()
    return {"mensaje": "Categoría eliminada correctamente"}

# Reactivar categoría
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

# Actualizar categoría
@router.put("/actualizar/{categoria_id}", response_model=CategoriaOut)
def actualizar_categoria(categoria_id: int, datos: CategoriaUpdate, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    categoria.nombre = datos.nombre
    db.commit()
    db.refresh(categoria)

    return categoria
