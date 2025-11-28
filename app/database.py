from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# CONFIGURACIÓN DE POSTGRES EN CLEVER CLOUD

DATABASE_URL ="postgresql://uf0ntmn4xj4krs28waqc:jjLZ1StjVHLCLFDHN9Lh2xrZZrHKqn@bndc4z5sb5gymmbazimh-postgresql.services.clever-cloud.com:50013/bndc4z5sb5gymmbazimh"


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

