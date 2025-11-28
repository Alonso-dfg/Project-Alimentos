from fastapi import FastAPI, Request
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

