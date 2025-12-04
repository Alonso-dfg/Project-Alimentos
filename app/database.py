from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://u0ppotytdpdmclcv9ilu:vjVsNVaasXQo7b2NcOETM9aQ0XuyBI@bqroardzwdqccmw3wj4k-postgresql.services.clever-cloud.com:50013/bqroardzwdqccmw3wj4k"

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
