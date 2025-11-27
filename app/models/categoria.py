from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)

    # Relación 1:N con productos
    productos = relationship("Producto", back_populates="categoria_relacion")
    estado = Column(String, default="activo")
