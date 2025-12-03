from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://u1c2tiai7lxtthta8brd:7lVTMC3WLQpACUokG7AZK5UoO3nHDH@bhrdihak9xywof9dezre-postgresql.services.clever-cloud.com:50013/bhrdihak9xywof9dezre"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
