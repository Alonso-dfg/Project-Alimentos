from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str
    correo: EmailStr
    telefono: str
    ciudad: str
    # imagen NO va aquí, porque se envía como UploadFile

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    imagen: Optional[str] = None   # nombre del archivo guardado, opcional

class UsuarioOut(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    telefono: str
    ciudad: str
    imagen: Optional[str] = None

    class Config:
        orm_mode = True
