from pydantic import BaseModel, EmailStr
from typing import Optional

# Datos necesarios para registrar un usuario nuevo
class UsuarioCreate(BaseModel):
    nombre: str
    correo: EmailStr        # Se valida que sea un correo real
    telefono: str
    ciudad: str
    # La imagen NO se coloca aquí porque se recibe como archivo (UploadFile)

# Datos opcionales para actualizar un usuario
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    imagen: Optional[str] = None   # Se guarda el nombre del archivo

# Datos que se devuelven cuando se muestra un usuario
class UsuarioOut(BaseModel):
    id: int               # Identificador del usuario en la BD
    nombre: str
    correo: EmailStr
    telefono: str
    ciudad: str
    imagen: Optional[str] = None   # Nombre o ruta de la imagen

    class Config:
        orm_mode = True  # Permite convertir objetos ORM a este modelo
