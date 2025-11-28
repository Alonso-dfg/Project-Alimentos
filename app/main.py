from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import Base, engine, get_db
from app.routers import productos, categorias, proveedores, usuario, externos

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title = "API de Alimentos - Proyecto Integrador")

# Incluir las rutas
app.include_router(productos.router)
app.include_router(categorias.router)
app.include_router(proveedores.router)
app.include_router(usuario.router)
app.include_router(externos.router)


templates = Jinja2Templates(directory = "templates")
app.mount("/static", StaticFiles(directory = "static"),name = "static")

@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    return templates.TemplateResponse(
        name = "index.html",
        request = request
    )


# === RUTAS HTML ===

@app.get("/productos-menu")
async def productos_menu(request: Request):
    return templates.TemplateResponse(
        name = "productos_menu.html",
        request = request
    )

# 1. Menú de productos
@app.get("/productos-menu")
def productos_menu(request: Request):
    return templates.TemplateResponse("productos_menu.html", {
        "request": request
    })


# 2. Ver todos los productos
@app.get("/vista-productos")
def vista_productos(request: Request, db: Session = Depends(get_db)):
    productos = db.query(productos).all()
    return templates.TemplateResponse("productos_lista.html", {
        "request": request,
        "productos": productos
    })


# 3. Crear producto (formulario HTML)
@app.get("/crear-producto")
def crear_producto_form(request: Request):
    return templates.TemplateResponse("producto_crear.html", {
        "request": request
    })


# 4. Buscar producto por ID (formulario)
@app.get("/buscar-producto")
def buscar_producto_form(request: Request):
    return templates.TemplateResponse("producto_buscar.html", {
        "request": request
    })


# 5. Actualizar producto por ID
@app.get("/actualizar-producto")
def actualizar_producto_form(request: Request):
    return templates.TemplateResponse("producto_actualizar.html", {
        "request": request
    })


# 6. Eliminar producto por ID
@app.get("/eliminar-producto")
def eliminar_producto_form(request: Request):
    return templates.TemplateResponse("producto_eliminar.html", {
        "request": request
    })


# 7. Subir imagen para un producto
@app.get("/subir-imagen")
def subir_imagen_form(request: Request):
    return templates.TemplateResponse("imagen_subir.html", {
        "request": request
    })