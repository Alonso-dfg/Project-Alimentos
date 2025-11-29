from pydantic import BaseModel
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    precio: float
    cantidad: int
    ciudad: str                      
    imagen: Optional[str] = None
    categoria_id: int
    proveedor_id: int
    usuario_id: int


class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: str | None = None
    precio: float | None = None
    cantidad: int | None = None
    ciudad: str | None = None
    categoria_id: int | None = None
    proveedor_id: int | None = None
    usuario_id: int | None = None
    imagen: str | None = None

class ProductoOut(ProductoBase):
    id: int
    estado: str

    class Config:
        orm_mode = True
