from pydantic import BaseModel
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    precio: float
    cantidad: int
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    proveedor_id: Optional[int] = None
    usuario_id: Optional[int] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(ProductoBase):
    pass

class ProductoOut(ProductoBase):
    id: int
    estado: str

    class Config:
        orm_mode = True