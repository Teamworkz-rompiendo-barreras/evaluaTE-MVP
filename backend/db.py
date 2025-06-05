# db.py
import os
import databases
import sqlalchemy
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del .env automáticamente

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Falta la variable DATABASE_URL en el .env")

# Creamos el objeto `database` para usar con `Databases` (asíncrono)
database = databases.Database(DATABASE_URL)

# Metadata para SQLAlchemy (por si luego queremos declarar tablas adicionales)
metadata = sqlalchemy.MetaData()
