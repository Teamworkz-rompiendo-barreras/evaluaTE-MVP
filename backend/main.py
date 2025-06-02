from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sqlalchemy
import shutil

from db import database
from generate_report import generar_informe as generar_informe_ia

app = FastAPI()

# Habilita CORS para permitir llamadas desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos que espera el endpoint
class DatosInforme(BaseModel):
    nombre: str
    apellidos: str
    email: str
    whatsapp: str

# Definición de la tabla "informes"
metadata = sqlalchemy.MetaData()

informes = sqlalchemy.Table(
    "informes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nombre", sqlalchemy.String(100)),
    sqlalchemy.Column("apellidos", sqlalchemy.String(100)),
    sqlalchemy.Column("email", sqlalchemy.String(150)),
    sqlalchemy.Column("whatsapp", sqlalchemy.String(20)),
    sqlalchemy.Column("resumen", sqlalchemy.Text),
    sqlalchemy.Column("fortalezas", sqlalchemy.Text),
    sqlalchemy.Column("areas_mejora", sqlalchemy.Text),
    sqlalchemy.Column("orientacion", sqlalchemy.Text),
    sqlalchemy.Column("conclusion", sqlalchemy.Text),
)

# Conectar a la base de datos al iniciar la app
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# NUEVO: Endpoint para subir el CV y guardarlo localmente
@app.post("/api/subir-cv")
async def subir_cv(file: UploadFile = File(...)):
    ruta_destino = f"uploads/{file.filename}"
    with open(ruta_destino, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"ruta_cv": ruta_destino}

# Endpoint que recibe los datos del formulario y genera el informe
@app.post("/api/generar-informe")
async def generar_informe_endpoint(datos: DatosInforme):
    datos_dict = datos.dict()

    # Ruta al CV: más adelante, deberías conectar con lo que devuelve /api/subir-cv
    datos_dict["ruta_cv"] = "uploads/cv_muestra.pdf"  # Sustituir por ruta real recibida desde el frontend

    # Resultados de minijuegos (por ahora simulados)
    datos_dict["resultados_minijuegos"] = "Comunicación alta, liderazgo medio, resolución de problemas alta."

    # Generar informe estructurado con IA
    informe = generar_informe_ia(datos_dict)

    # Guardar en base de datos
    query = informes.insert().values(
        nombre=datos_dict.get("nombre", ""),
        apellidos=datos_dict.get("apellidos", ""),
        email=datos_dict.get("email", ""),
        whatsapp=datos_dict.get("whatsapp", ""),
        resumen=informe.get("resumen", ""),
        fortalezas=", ".join(informe.get("fortalezas", [])),
        areas_mejora=", ".join(informe.get("areas_mejora", [])),
        orientacion=informe.get("orientacion", ""),
        conclusion=informe.get("conclusion", "")
    )
    await database.execute(query)

    # Devolver informe al frontend
    return JSONResponse(content={"informe": {
        "nombre": datos_dict.get("nombre", ""),
        "apellidos": datos_dict.get("apellidos", ""),
        "email": datos_dict.get("email", ""),
        "whatsapp": datos_dict.get("whatsapp", ""),
        "resumen": informe.get("resumen", ""),
        "fortalezas": informe.get("fortalezas", []),
        "areas_mejora": informe.get("areas_mejora", []),
        "orientacion": informe.get("orientacion", ""),
        "conclusion": informe.get("conclusion", "")
    }})

# Ejecutar localmente
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
