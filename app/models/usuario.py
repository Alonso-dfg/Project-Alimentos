from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String, index=True)
    correo = Column(String, unique=True, index=True)
    telefono = Column(String)
    ciudad = Column(String)
    imagen = Column(String, nullable=True)

    productos = relationship("Producto", back_populates="usuario")

    estado = Column(String, default="activo")