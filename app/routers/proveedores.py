from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.producto import Producto
from app.models.proveedor import Proveedor
from app.schemas.proveedor_schema import ProveedorCreate, ProveedorOut
from typing import List

# Router principal para todo lo relacionado con proveedores
router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

# Carpeta donde están las plantillas HTML
templates = Jinja2Templates(directory="app/templates")


"""
=======================================
      SECCIÓN DE RUTAS HTML (VISTAS)
=======================================
"""


# ------- Página con opciones del módulo -------
@router.get("/opciones", response_class=HTMLResponse)
async def opciones_proveedores(request: Request):
    # Solo muestra el menú principal de proveedores
    return templates.TemplateResponse("proveedores/opciones.html", {"request": request})


# ------- Listar proveedores activos -------
@router.get("/listar", response_class=HTMLResponse)
async def listar_proveedores_html(request: Request, db: Session = Depends(get_db)):
    # Se consultan solo proveedores con estado activo
    proveedores = db.query(Proveedor).filter(Proveedor.estado == "activo").all()

    return templates.TemplateResponse(
        "proveedores/listar_proveedores.html",
        {"request": request, "proveedores": proveedores}
    )


# ------- Listar proveedores inactivos -------
@router.get("/inactivos", response_class=HTMLResponse)
async def listar_inactivos_html(request: Request, db: Session = Depends(get_db)):
    proveedores = db.query(Proveedor).filter(Proveedor.estado == "inactivo").all()

    return templates.TemplateResponse(
        "proveedores/listar_proveedores_inactivos.html",
        {"request": request, "proveedores": proveedores}
    )


# ------- Reactivar un proveedor inactivo -------
@router.post("/reactivar", response_class=HTMLResponse)
async def reactivar_proveedor(
    request: Request,
    id: int = Form(...),  # El ID llega desde un formulario HTML
    db: Session = Depends(get_db)
):
    # Buscar el proveedor
    proveedor = db.query(Proveedor).filter(Proveedor.id == id).first()

    if not proveedor:
        # Si no existe, se vuelve a mostrar la tabla con un mensaje
        proveedores = db.query(Proveedor).filter(Proveedor.estado == "inactivo").all()
        return templates.TemplateResponse(
            "proveedores/listar_proveedores_inactivos.html",
            {"request": request, "proveedores": proveedores, "mensaje": "Proveedor no encontrado"}
        )

    # Cambio de estado
    proveedor.estado = "activo"
    db.commit()

    # Redirección para evitar reenvío de formulario
    return RedirectResponse("/proveedores/inactivos", status_code=303)


# ------- Formulario para buscar proveedor -------
@router.get("/buscar", response_class=HTMLResponse)
async def buscar_proveedor_form(request: Request):
    return templates.TemplateResponse("proveedores/buscar_proveedor.html", {"request": request})


# ------- Buscar proveedor por ID -------
@router.post("/buscar", response_class=HTMLResponse)
async def buscar_proveedor_post(request: Request, id: int = Form(...), db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.id == id).first()

    return templates.TemplateResponse(
        "proveedores/buscar_proveedor.html",
        {
            "request": request,
            "proveedor": proveedor,
            "mensaje": "Proveedor no encontrado" if not proveedor else None
        }
    )


# ------- Formulario para crear proveedor -------
@router.get("/crear", response_class=HTMLResponse)
async def crear_form(request: Request):
    return templates.TemplateResponse("proveedores/crear_proveedor.html", {"request": request})


# ------- Crear proveedor -------
@router.post("/crear", response_class=HTMLResponse)
async def crear_post(
    request: Request,
    nombre: str = Form(...),
    contacto: str = Form(...),
    telefono: str = Form(...),
    correo: str = Form(...),
    ciudad: str = Form(...),
    db: Session = Depends(get_db)
):
    # Se crea el objeto proveedor con los datos del formulario
    nuevo_proveedor = Proveedor(
        nombre=nombre,
        contacto=contacto,
        telefono=telefono,
        ciudad=ciudad,
        correo=correo,
        estado="activo"
    )

    db.add(nuevo_proveedor)
    db.commit()
    db.refresh(nuevo_proveedor)

    return RedirectResponse("/proveedores/listar", status_code=303)


# ------- Formulario para editar proveedor -------
@router.get("/editar", response_class=HTMLResponse)
async def editar_proveedor_form(request: Request):
    return templates.TemplateResponse("proveedores/actualizar_proveedor.html", {"request": request})


# ------- Editar proveedor -------
@router.post("/editar", response_class=HTMLResponse)
async def editar_proveedor_post(
    request: Request,
    id: int = Form(...),
    nombre: str = Form(...),
    telefono: str = Form(...),
    correo: str = Form(None),      # Opcional
    direccion: str = Form(None),   # Opcional
    db: Session = Depends(get_db)
):
    proveedor = db.query(Proveedor).filter(Proveedor.id == id).first()

    if not proveedor:
        return templates.TemplateResponse(
            "proveedores/actualizar_proveedor.html",
            {"request": request, "mensaje": "Proveedor no encontrado"}
        )

    # Solo se actualizan los campos enviados
    proveedor.nombre = nombre
    proveedor.telefono = telefono
    if correo:
        proveedor.correo = correo
    if direccion:
        proveedor.direccion = direccion

    db.commit()
    db.refresh(proveedor)

    return RedirectResponse("/proveedores/listar", status_code=303)


# ------- Formulario para eliminar proveedor -------
@router.get("/eliminar", response_class=HTMLResponse)
async def eliminar_proveedor_form(request: Request):
    return templates.TemplateResponse("proveedores/eliminar_proveedor.html", {"request": request})


# ------- Eliminar proveedor (se marca como inactivo) -------
@router.post("/eliminar", response_class=HTMLResponse)
async def eliminar_proveedor_post(
    request: Request,
    id: int = Form(...),
    db: Session = Depends(get_db)
):
    proveedor = db.query(Proveedor).filter(Proveedor.id == id).first()

    if not proveedor:
        return templates.TemplateResponse(
            "proveedores/eliminar_proveedor.html",
            {"request": request, "mensaje": "Proveedor no encontrado"}
        )

    # Solo productos activos bloquean la eliminación
    relacionado = db.query(Producto).filter(
        Producto.proveedor_id == id,
        Producto.estado == "activo"
    ).first()

    if relacionado:
        return templates.TemplateResponse(
            "proveedores/eliminar_proveedor.html",
            {
                "request": request,
                "mensaje": "No se puede eliminar: proveedor asociado a productos ACTIVOS."
            }
        )

    # Se marca como inactivo para mantener registro histórico
    proveedor.estado = "inactivo"
    db.commit()

    return RedirectResponse("/proveedores/listar", status_code=303)


"""
=======================================
         SECCIÓN DE RUTAS API
=======================================
"""


# ------- API: Listar activos -------
@router.get("/api", response_model=List[ProveedorOut])
def listar_proveedores_api(db: Session = Depends(get_db)):
    return db.query(Proveedor).filter(Proveedor.estado == "activo").all()


# ------- API: Listar inactivos -------
@router.get("/api/inactivos", response_model=List[ProveedorOut])
def listar_proveedores_inactivos_api(db: Session = Depends(get_db)):
    return db.query(Proveedor).filter(Proveedor.estado == "inactivo").all()


# ------- API: Obtener proveedor específico -------
@router.get("/api/{proveedor_id}", response_model=ProveedorOut)
def obtener_proveedor_api(proveedor_id: int, db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()

    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    return proveedor


# ------- API: Crear proveedor -------
@router.post("/api/", response_model=ProveedorOut)
def crear_proveedor_api(proveedor: ProveedorCreate, db: Session = Depends(get_db)):
    nuevo = Proveedor(**proveedor.dict())

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


# ------- API: Actualizar proveedor -------
@router.put("/api/{proveedor_id}", response_model=ProveedorOut)
def actualizar_proveedor_api(proveedor_id: int, proveedor_actualizado: ProveedorCreate, db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()

    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    # Actualiza cada campo automáticamente
    for key, value in proveedor_actualizado.dict().items():
        setattr(proveedor, key, value)

    db.commit()
    db.refresh(proveedor)

    return proveedor


# ------- API: Eliminar proveedor (inactivar) -------
@router.delete("/api/{proveedor_id}")
def eliminar_proveedor_api_endpoint(proveedor_id: int, db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()

    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    relacionado = db.query(Producto).filter(Producto.proveedor_id == proveedor_id).first()

    if relacionado:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar: proveedor asociado a productos."
        )

    proveedor.estado = "inactivo"
    db.commit()

    return {"mensaje": "Proveedor inactivado correctamente"}


# ------- API: Reactivar proveedor -------
@router.put("/api/reactivar/{proveedor_id}", response_model=ProveedorOut)
def reactivar_proveedor_api(proveedor_id: int, db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()

    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    proveedor.estado = "activo"
    db.commit()
    db.refresh(proveedor)

    return proveedor
