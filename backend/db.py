# backend/db.py

import os
import sqlalchemy
import databases
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Cargar la URL de la base de datos desde variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("No se encontró la variable de entorno DATABASE_URL")

# Instancia de `databases` para conexión asíncrona
database = databases.Database(DATABASE_URL)

# Metadatos para SQLAlchemy
metadata = sqlalchemy.MetaData()

# Definición de la tabla “informes” (SQLAlchemy)
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
    sqlalchemy.Column("cv_text", sqlalchemy.Text),              # Texto completo extraído del PDF
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
