from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# CONFIGURACIÓN DE POSTGRES EN CLEVER CLOUD

DATABASE_URL ="postgresql://ugnhwlflrumhtotqhxv7:Mo3Yd6vyUW3S50Q9M887582fALYPrZ@blbbxpb9ooq87tnvbs7t-postgresql.services.clever-cloud.com:50013/blbbxpb9ooq87tnvbs7t"


# Crear engine de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=True,         
    pool_pre_ping=True  # mantiene conexiones vivas
)

# Crear sesión
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener DB en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

