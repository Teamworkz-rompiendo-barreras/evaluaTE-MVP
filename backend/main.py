from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sqlalchemy
import shutil
import os

from db import database
from generate_report import generar_informe as generar_informe_ia

app = FastAPI()

# CORS para permitir llamadas del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de entrada
class DatosInforme(BaseModel):
    nombre: str
    apellidos: str
    email: str
    whatsapp: str
    cv_filename: str  # <-- Nuevo campo: nombre del archivo PDF del CV

# Estructura de la base de datos
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

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Endpoint para subir el CV
@app.post("/api/subir-cv")
async def subir_cv(file: UploadFile = File(...)):
    ruta_destino = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(ruta_destino, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"ruta_cv": ruta_destino, "filename": file.filename}

# Endpoint para generar el informe de empleabilidad
@app.post("/api/generar-informe")
async def generar_informe_endpoint(datos: DatosInforme):
    datos_dict = datos.dict()

    ruta_cv = f"uploads/{datos_dict.get('cv_filename', '')}"
    resultados = "Comunicación alta, resolución media, liderazgo bajo"  # Simulado por ahora

    # Construimos el diccionario completo
    datos_completos = {
        "nombre": datos_dict.get("nombre", ""),
        "apellidos": datos_dict.get("apellidos", ""),
        "email": datos_dict.get("email", ""),
        "whatsapp": datos_dict.get("whatsapp", ""),
        "ruta_cv": ruta_cv,
        "resultados_minijuegos": resultados
    }

    informe = generar_informe_ia(datos_completos)

    # Guardamos el informe
    query = informes.insert().values(
        nombre=datos_completos["nombre"],
        apellidos=datos_completos["apellidos"],
        email=datos_completos["email"],
        whatsapp=datos_completos["whatsapp"],
        resumen=informe.get("resumen", ""),
        fortalezas=", ".join(informe.get("fortalezas", [])),
        areas_mejora=", ".join(informe.get("areas_mejora", [])),
        orientacion=informe.get("orientacion", ""),
        conclusion=informe.get("conclusion", "")
    )
    await database.execute(query)

    return JSONResponse(content={"informe": {
        "nombre": datos_completos["nombre"],
        "apellidos": datos_completos["apellidos"],
        "email": datos_completos["email"],
        "whatsapp": datos_completos["whatsapp"],
        "resumen": informe.get("resumen", ""),
        "fortalezas": informe.get("fortalezas", []),
        "areas_mejora": informe.get("areas_mejora", []),
        "orientacion": informe.get("orientacion", ""),
        "conclusion": informe.get("conclusion", "")
    }})

# Ejecutar localmente
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

