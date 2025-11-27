from pydantic import BaseModel
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    categoria_id: Optional[float] = None  
    proveedor_id: Optional[float] = None  
    usuario_id: Optional[float] = None    
    precio: float
    ciudad: str
    fuente: str

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(ProductoBase):
    pass

class ProductoOut(ProductoBase):
    id: int
    estado: str

    class Config:
        orm_mode = True