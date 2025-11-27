from pydantic import BaseModel

class ProveedorBase(BaseModel):
    nombre: str
    contacto: str
    telefono: float
    ciudad: str

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorOut(ProveedorBase):
    id: int

    class Config:
        orm_mode = True
