from pydantic import BaseModel


# Esquema base: define los campos comunes que comparten
# las categorías en las operaciones (crear, mostrar, actualizar).

class CategoriaBase(BaseModel):
    nombre: str  # Nombre de la categoría


# Esquema usado cuando se crea una categoría.
# Hereda los campos del esquema base, así evitamos repetir código.

class CategoriaCreate(CategoriaBase):
    pass  # No necesita campos adicionales


# Esquema que se usa para devolver datos al cliente.
# Incluye el "id" porque ese valor sí existe en la base de datos.

class CategoriaOut(CategoriaBase):
    id: int  # ID asignado por la BD

    # Permite que Pydantic lea objetos ORM como los de SQLAlchemy
    class Config:
        orm_mode = True


# Esquema para actualizar una categoría existente.
# Solo permitimos cambiar el nombre.

class CategoriaUpdate(BaseModel):
    nombre: str
