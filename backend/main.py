# backend/main.py

import os
from io import BytesIO

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from pydantic import BaseModel
import uvicorn
import sqlalchemy
import PyPDF2
from dotenv import load_dotenv

from db import database  # Asegúrate de que db.py exporta 'database' y la MetaData si la necesitas
from generate_report import generar_informe as generar_informe_ia

# ---------------------------------------------------
# CARGA DE VARIABLES DE ENTORNO
# ---------------------------------------------------
load_dotenv()
# (Opcionalmente, valida aquí que las variables obligatorias existen)

# ---------------------------------------------------
# INICIALIZACIÓN DE FastAPI
# ---------------------------------------------------
app = FastAPI()

# ---------------------------------------------------
# MIDDLEWARE para CORS + Access-Control-Allow-Private-Network
# ---------------------------------------------------
#  1) Configuramos CORS “normal”
#  2) Añadimos UN middleware adicional para inyectar
#     Access-Control-Allow-Private-Network: true en cada respuesta.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # Permitir todos los orígenes (ajusta si quieres restringir dominios)
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware adicional para Private Network Access
@app.middleware("http")
async def add_private_network_header(request: Request, call_next):
    response: Response = await call_next(request)
    # Inyectamos el header necesario para “Private Network Access”
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

# ---------------------------------------------------
# DEFINICIÓN DE MODELO DE DATOS (Pydantic)
# ---------------------------------------------------
class DatosInforme(BaseModel):
    nombre: str
    apellidos: str
    email: str
    whatsapp: str
    discapacidad: str = ""
    tipo: str = ""
    puesto: str = ""
    jornada: str = ""
    disponibilidad: str = ""
    traslado: str = ""
    minijuego_decisiones_score: str = ""
    minijuego_resolucion_score: str = ""
    minijuego_comunicacion_score: str = ""
    minijuego_adaptabilidad_score: str = ""
    minijuego_tiempo_score: str = ""
    minijuego_equipo_score: str = ""
    minijuego_creatividad_score: str = ""
    minijuego_liderazgo_score: str = ""
    minijuego_pensamiento_score: str = ""
    minijuego_emocional_score: str = ""
    cv_text: str  # Este campo contendrá el texto extraído del PDF

# ---------------------------------------------------
# CONFIGURACIÓN DE LA TABLA “informes” con SQLAlchemy
# ---------------------------------------------------
metadata = sqlalchemy.MetaData()

informes = sqlalchemy.Table(
    "informes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
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
    sqlalchemy.Column("cv_text", sqlalchemy.Text),  # Guardamos texto del CV
    sqlalchemy.Column("minijuego_decisiones_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_resolucion_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_comunicacion_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_adaptabilidad_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_tiempo_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_equipo_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_creatividad_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_liderazgo_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_pensamiento_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_emocional_score", sqlalchemy.Text),
    sqlalchemy.Column("resumen", sqlalchemy.Text),
    sqlalchemy.Column("fortalezas", sqlalchemy.Text),
    sqlalchemy.Column("areas_mejora", sqlalchemy.Text),
    sqlalchemy.Column("orientacion", sqlalchemy.Text),
    sqlalchemy.Column("conclusion", sqlalchemy.Text),
)

# ---------------------------------------------------
# Eventos de inicio y cierre de FastAPI para la DB
# ---------------------------------------------------
@app.on_event("startup")
async def startup():
    await database.connect()
    # Crear las tablas si no existen (solo en desarrollo; en producción usa migrations)
    engine = sqlalchemy.create_engine(str(database.url).replace('+asyncpg', ''))
    metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ---------------------------------------------------
# ENDPOINT 1: Subir el CV (PDF)
# ---------------------------------------------------
@app.post("/api/subir-cv")
async def subir_cv(file: UploadFile = File(...)):
    """
    Recibe un PDF, extrae su texto usando PyPDF2 y devuelve { "cv_text": "..." }.
    """
    contenido = await file.read()
    try:
        # Extraer texto página a página
        reader = PyPDF2.PdfReader(BytesIO(contenido))
        texto_completo = []
        for página in reader.pages:
            texto_página = página.extract_text() or ""
            texto_completo.append(texto_página)
        texto_unido = "\n".join(texto_completo).strip()
    except Exception as e:
        # Si falla la extracción, devolvemos un mensaje mínimo
        texto_unido = ""
        print("⚠️ No se pudo extraer texto del PDF:", e)

    return {"cv_text": texto_unido}

# ---------------------------------------------------
# ENDPOINT 2: Generar Informe (usa TODO: datos + texto del CV)
# ---------------------------------------------------
@app.post("/api/generar-informe")
async def generar_informe_endpoint(datos: DatosInforme):
    datos_dict = datos.dict()

    # ---------------------------------------------------
    # Construir el “prompt” completo que se pasará a la IA,
    # concatenando todos los campos en un solo string.
    # ---------------------------------------------------
    perfil = f"""
Nombre: {datos_dict['nombre']} {datos_dict['apellidos']}
Email: {datos_dict['email']}
WhatsApp: {datos_dict['whatsapp']}
Discapacidad: {datos_dict['discapacidad']}
Modalidad: {datos_dict['tipo']}
Puesto deseado: {datos_dict['puesto']}
Jornada: {datos_dict['jornada']}
Disponibilidad: {datos_dict['disponibilidad']}
Traslado: {datos_dict['traslado']}

Texto extraído de CV:
{datos_dict['cv_text']}

Resultados de habilidades blandas:
- Toma de decisiones: {datos_dict['minijuego_decisiones_score']}
- Resolución de problemas: {datos_dict['minijuego_resolucion_score']}
- Comunicación: {datos_dict['minijuego_comunicacion_score']}
- Adaptabilidad: {datos_dict['minijuego_adaptabilidad_score']}
- Gestión del tiempo: {datos_dict['minijuego_tiempo_score']}
- Trabajo en equipo: {datos_dict['minijuego_equipo_score']}
- Creatividad: {datos_dict['minijuego_creatividad_score']}
- Liderazgo: {datos_dict['minijuego_liderazgo_score']}
- Pensamiento crítico: {datos_dict['minijuego_pensamiento_score']}
- Inteligencia emocional: {datos_dict['minijuego_emocional_score']}
"""

    # Llamamos a la función que invoca a AzureOpenAI
    texto_completo = generar_informe_ia(perfil)

    # ---------------------------------------------------
    # A partir del texto completo ANTES de guardarlo,
    # vamos a extraer las secciones (Resumen, Fortalezas, etc.)
    # de acuerdo a los indicadores que definimos en el prompt.
    # ---------------------------------------------------
    resumen = ""
    fortalezas = []
    mejoras = []
    orientacion = ""
    conclusion = ""

    # El texto devuelto por la IA tiene esta estructura (aprox):
    # 1. RESUMEN PERSONAL
    # (un párrafo breve)
    #
    # 2. FORTALEZAS
    # - Fortaleza 1
    # - Fortaleza 2
    #
    # 3. OPORTUNIDADES DE MEJORA
    # - Mejora 1
    # ...
    #
    # 4. ORIENTACIÓN LABORAL PERSONALIZADA
    # (algun texto)
    #
    # 5. CONCLUSIÓN POSITIVA
    # (algun texto)

    # Vamos a segmentar línea a línea:
    líneas = texto_completo.splitlines()
    sección_actual = None

    for linea in líneas:
        texto = linea.strip()
        if not texto:
            continue

        # Detectar inicio de cada sección mayor
        if texto.lower().startswith("resumen personal"):
            sección_actual = "resumen"
            continue
        if texto.lower().startswith("fortalezas"):
            sección_actual = "fortalezas"
            continue
        if texto.lower().startswith("oportunidades de mejora"):
            sección_actual = "mejoras"
            continue
        if texto.lower().startswith("orientación laboral"):
            sección_actual = "orientacion"
            continue
        if texto.lower().startswith("conclusión"):
            sección_actual = "conclusion"
            continue

        # Según la sección actual, vamos guardando el contenido
        if sección_actual == "resumen":
            resumen += texto + " "
        elif sección_actual == "fortalezas":
            if texto.startswith("-") or texto.startswith("•"):
                fortalezas.append(texto.lstrip("-• ").strip())
        elif sección_actual == "mejoras":
            if texto.startswith("-") or texto.startswith("•"):
                mejoras.append(texto.lstrip("-• ").strip())
        elif sección_actual == "orientacion":
            orientacion += texto + " "
        elif sección_actual == "conclusion":
            conclusion += texto + " "

    resumen = resumen.strip()
    orientacion = orientacion.strip()
    conclusion = conclusion.strip()

    # ---------------------------------------------------
    # Construir el JSON con el informe que enviaremos al front
    # ---------------------------------------------------
    informe = {
        "nombre": datos_dict["nombre"],
        "apellidos": datos_dict["apellidos"],
        "email": datos_dict["email"],
        "whatsapp": datos_dict["whatsapp"],
        "jornada": datos_dict["jornada"],
        "disponibilidad": datos_dict["disponibilidad"],
        "discapacidad": datos_dict["discapacidad"],
        "tipo": datos_dict["tipo"],
        "puesto": datos_dict["puesto"],
        "resumen": resumen,
        "fortalezas": fortalezas,
        "areas_mejora": mejoras,
        "orientacion": orientacion,
        "conclusion": conclusion,
    }

    # ---------------------------------------------------
    # Guardar en la base de datos (incluyendo todos los campos)
    # ---------------------------------------------------
    query = informes.insert().values(
        nombre=informe["nombre"],
        apellidos=informe["apellidos"],
        email=informe["email"],
        whatsapp=informe["whatsapp"],
        discapacidad=datos_dict["discapacidad"],
        tipo=datos_dict["tipo"],
        puesto=datos_dict["puesto"],
        jornada=datos_dict["jornada"],
        disponibilidad=datos_dict["disponibilidad"],
        traslado=datos_dict["traslado"],
        cv_text=datos_dict["cv_text"],
        minijuego_decisiones_score=datos_dict["minijuego_decisiones_score"],
        minijuego_resolucion_score=datos_dict["minijuego_resolucion_score"],
        minijuego_comunicacion_score=datos_dict["minijuego_comunicacion_score"],
        minijuego_adaptabilidad_score=datos_dict["minijuego_adaptabilidad_score"],
        minijuego_tiempo_score=datos_dict["minijuego_tiempo_score"],
        minijuego_equipo_score=datos_dict["minijuego_equipo_score"],
        minijuego_creatividad_score=datos_dict["minijuego_creatividad_score"],
        minijuego_liderazgo_score=datos_dict["minijuego_liderazgo_score"],
        minijuego_pensamiento_score=datos_dict["minijuego_pensamiento_score"],
        minijuego_emocional_score=datos_dict["minijuego_emocional_score"],
        resumen=informe["resumen"],
        fortalezas=", ".join(informe["fortalezas"]),
        areas_mejora=", ".join(informe["areas_mejora"]),
        orientacion=informe["orientacion"],
        conclusion=informe["conclusion"],
    )
    await database.execute(query)

    return JSONResponse(content={"informe": informe})

# ---------------------------------------------------
# Para desarrollo local:
# ---------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
