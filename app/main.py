from fastapi import FastAPI
from app.database import Base, engine
from app.routers import productos, categorias, proveedores, usuario, externos

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title = "API Productos - Proyecto Integrador")

# Incluir las rutas
app.include_router(productos.router)
app.include_router(categorias.router)
app.include_router(proveedores.router)
app.include_router(usuario.router)
app.include_router(externos.router)

@app.get("/")
def inicio():
    return {"mensaje": "API funcionando "}
