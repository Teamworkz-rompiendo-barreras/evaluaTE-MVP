from sqlalchemy import create_engine, MetaData
from databases import Database

# Cambia estos datos por los tuyos
DATABASE_URL = "postgresql://esteadmin:EvaluaTE2025@evaluatete-db.postgres.database.azure.com:5432/postgres"

database = Database(DATABASE_URL)
metadata = MetaData()

engine = create_engine(DATABASE_URL)
