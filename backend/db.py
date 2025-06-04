# backend/db.py

import os
from dotenv import load_dotenv
import databases
import sqlalchemy

# ---------------------------------------------------
# CARGAR VARIABLES DE ENTORNO
# ---------------------------------------------------
load_dotenv()

# Este es tu DATABASE_URL (ya con “+asyncpg” si vas a usar asyncpg)
# Por ejemplo: 
# postgresql+asyncpg://usuario:clave@<tu-host>.postgres.database.azure.com:5432/<tu-db>
DATABASE_URL = os.getenv("DATABASE_URL")

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
