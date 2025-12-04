from pydantic import BaseModel
from typing import Optional

# Esquema base del producto. 

class ProductoBase(BaseModel):
    nombre: str                     # Nombre del producto
    precio: float                   # Precio unitario
    cantidad: int                   # Existencias disponibles
    ciudad: str                     # Ciudad donde se encuentra
    imagen: Optional[str] = None    # URL o nombre del archivo (opcional)
    categoria_id: int               # Relación con la categoría
    proveedor_id: int               # Relación con el proveedor
    usuario_id: Optional[int] = None  # Usuario que lo registró (opcional)



# Esquema usado al momento de crear un producto nuevo.

class ProductoCreate(ProductoBase):
    pass


# Esquema para actualizar un producto.

class ProductoUpdate(BaseModel):
    nombre: str | None = None
    precio: float | None = None
    cantidad: int | None = None
    ciudad: str | None = None
    categoria_id: int | None = None
    proveedor_id: int | None = None
    usuario_id: int | None = None
    imagen: str | None = None


# Esquema que se usa cuando la API devuelve información 

class ProductoOut(ProductoBase):
    id: int               # Identificador del producto en la BD
    estado: str           # Estado del producto (activo/inactivo)

    # Permite que Pydantic lea objetos ORM como los de SQLAlchemy
    class Config:
        orm_mode = True
