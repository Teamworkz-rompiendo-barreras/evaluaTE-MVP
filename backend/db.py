import databases
import sqlalchemy

# ⚠️ Asegúrate de que estos datos coinciden con los de tu instalación de PostgreSQL
DATABASE_URL = "postgresql://postgres:EvaluaTE2025@localhost:5432/evaludate-db"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
