import os
import databases
import sqlalchemy

# ⚠️ Asegúrate de que estos datos coinciden con los de tu instalación de PostgreSQL
#    Se lee primero de la variable de entorno DATABASE_URL, y si no existe,
#    se usa un valor por defecto (local).
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:EvaluaTE2025@localhost:5432/evaludate-db"
)

# Creamos el objeto Database que usará asyncpg internamente
database = databases.Database(DATABASE_URL)

# Metadata para SQLAlchemy (si en el futuro quieres crear tablas desde aquí)
metadata = sqlalchemy.MetaData()
