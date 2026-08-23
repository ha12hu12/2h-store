from .config import settings

#Create engine
from sqlalchemy import create_engine
SQL_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQL_DATABASE_URL)

#Create a sessions factory
from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False ,bind=engine)

#Create (base) variable to inherit from in models
from sqlalchemy.orm import declarative_base
Base = declarative_base()

#get_db func
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

