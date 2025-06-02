import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from databases import Database

# Cargar variables del entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Conexión a la base de datos
database = Database(DATABASE_URL)
metadata = MetaData()

# Definición de la tabla 'informes'
informes = Table(
    "informes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nombre", String(100)),
    Column("apellidos", String(100)),
    Column("email", String(150)),
    Column("whatsapp", String(20)),
    Column("resumen", Text),
    Column("fortalezas", Text),
    Column("areas_mejora", Text),
    Column("orientacion", Text),
    Column("conclusion", Text),
    Column("fecha", TIMESTAMP, server_default=func.now()),
)

# Motor para uso con SQLAlchemy si se necesitara
engine = create_engine(DATABASE_URL)
