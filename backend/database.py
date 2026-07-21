# backend/database.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. RUTAS ABSOLUTAS: Encontramos la carpeta exacta de este archivo
directorio_actual = Path(__file__).resolve().parent
ruta_env = directorio_actual / ".env"

# Forzamos la lectura de ese archivo concreto
load_dotenv(dotenv_path=ruta_env)

logger = logging.getLogger(__name__)

# 2. AHORA SÍ, LEEMOS LA VARIABLE
DATABASE_URL = os.getenv("DATABASE_URL")

# 3. FRENO DE EMERGENCIA MEJORADO
if not DATABASE_URL:
    logger.critical(f"No se pudo cargar DATABASE_URL. Buscando en: {ruta_env}")
    raise ValueError(f"Error crítico: DATABASE_URL no encontrada. El sistema la ha buscado exactamente en la ruta: {ruta_env}. Verifica que la variable esté dentro y que el archivo no se llame '.env.txt' oculto.")

# 4. MOTOR DE BASE DE DATOS
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300, # Evita el cierre de conexiones en la nube
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        