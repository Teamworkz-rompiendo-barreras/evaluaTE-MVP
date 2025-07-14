# backend/db.py

import os
from dotenv import load_dotenv      # ① Importamos la función load_dotenv 
import sqlalchemy
import databases
from sqlalchemy.dialects.postgresql import UUID
import uuid

# ────────────────────────────────────────────────────────────────────────────────
# ① Cargamos las variables definidas en un fichero `.env` situado en esta carpeta.
#    load_dotenv() buscará automáticamente un `.env` en el mismo directorio (o en padres,
#    si no lo encuentra) y volcará esas claves a os.environ.
load_dotenv()
# ────────────────────────────────────────────────────────────────────────────────

# ② Leemos la URL de conexión a la base de datos desde la variable de entorno.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Si no existe, arrojamos un error claro para saber que faltó configurar .env
    raise RuntimeError(
        "No se encontró la variable de entorno DATABASE_URL. "
        "Asegúrate de que exista un fichero `.env` con la línea:\n\n"
        "    DATABASE_URL=postgresql+asyncpg://<usuario>:<clave>@<host>:<puerto>/<bd>\n"
    )

# ③ Creamos la instancia 'database' para conexiones asíncronas con el paquete 'databases'
database = databases.Database(DATABASE_URL)

# ④ Metadata de SQLAlchemy (se usará para crear/gestionar tablas)
metadata = sqlalchemy.MetaData()

# ────────────────────────────────────────────────────────────────────────────────
# ⑤ Definición de la tabla “informes”
#    Que debe coincidir con la estructura real en Postgres/Azure.
informes = sqlalchemy.Table(
    "informes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", UUID(as_uuid=True), default=uuid.uuid4, nullable=False),
    sqlalchemy.Column("nombre", sqlalchemy.String(100)),
    sqlalchemy.Column("apellidos", sqlalchemy.String(100)),
    sqlalchemy.Column("email", sqlalchemy.String(150)),
    sqlalchemy.Column("whatsapp", sqlalchemy.String(20)),
    sqlalchemy.Column("discapacidad", sqlalchemy.Text),
    sqlalchemy.Column("tipo", sqlalchemy.Text),
    sqlalchemy.Column("puesto", sqlalchemy.Text),
    sqlalchemy.Column("jornada", sqlalchemy.Text),
    sqlalchemy.Column("disponibilidad", sqlalchemy.Text),
    sqlalchemy.Column("traslado", sqlalchemy.Text),
    sqlalchemy.Column("cv_text", sqlalchemy.Text),              # Texto extraído del PDF
    sqlalchemy.Column("decision_score", sqlalchemy.Integer),
    sqlalchemy.Column("resolucion_score", sqlalchemy.Integer),
    sqlalchemy.Column("comunicacion_score", sqlalchemy.Integer),
    sqlalchemy.Column("adaptabilidad_score", sqlalchemy.Integer),
    sqlalchemy.Column("tiempo_score", sqlalchemy.Integer),
    sqlalchemy.Column("equipo_score", sqlalchemy.Integer),
    sqlalchemy.Column("creatividad_score", sqlalchemy.Integer),
    sqlalchemy.Column("liderazgo_score", sqlalchemy.Integer),
    sqlalchemy.Column("pensamiento_score", sqlalchemy.Integer),
    sqlalchemy.Column("emocional_score", sqlalchemy.Integer),
    sqlalchemy.Column("resumen", sqlalchemy.Text),
    sqlalchemy.Column("fortalezas", sqlalchemy.Text),
    sqlalchemy.Column("areas_mejora", sqlalchemy.Text),
    sqlalchemy.Column("orientacion", sqlalchemy.Text),
    sqlalchemy.Column("conclusion", sqlalchemy.Text),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
)
# ────────────────────────────────────────────────────────────────────────────────
# Al importar db.py, creará automáticamente las tablas que falten
from sqlalchemy import create_engine

# Convertimos tu URL asyncpg a una URL para create_engine
sync_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

# Creamos un engine síncrono y levantamos las tablas que falten
engine = create_engine(sync_url, echo=True)  
metadata.create_all(engine)
