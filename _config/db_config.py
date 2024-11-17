from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar las variables de entorno
load_dotenv()

# Obtener los datos de conexión desde el .env
DB_HOST = os.getenv("DB_HOST_TEST")
DB_PORT = os.getenv("DB_PORT_TEST")
DB_USER = os.getenv("DB_USER_TEST")
DB_PASSWORD = os.getenv("DB_PASSWORD_TEST")
DB_NAME = os.getenv("DB_NAME_TEST")

# Crear la URL de conexión
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configurar SQLAlchemy Engine y Session
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Context manager para obtener sesiones
def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()