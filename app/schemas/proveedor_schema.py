from pydantic import BaseModel

# Modelo base con los datos que tiene cualquier proveedor
class ProveedorBase(BaseModel):
    nombre: str
    contacto: str        # Persona o correo de contacto
    telefono: float      # Número telefónico
    ciudad: str          # Ciudad del proveedor

# Modelo para crear un proveedor nuevo (usa los mismos campos)
class ProveedorCreate(ProveedorBase):
    pass

# Modelo usado para mostrar datos al usuario
class ProveedorOut(ProveedorBase):
    id: int              # ID del proveedor en la base de datos

    class Config:
        orm_mode = True  # Permite leer datos desde modelos ORM
