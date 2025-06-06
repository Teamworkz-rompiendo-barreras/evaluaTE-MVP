# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sqlalchemy

from db import database
from generate_report import generar_informe as generar_informe_ia

# ─── 1) Crear la aplicación FastAPI y habilitar CORS ───
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Permitir peticiones desde cualquier origen (útil en desarrollo)
    allow_credentials=True,
    allow_methods=["*"],        # Permitir todos los métodos HTTP
    allow_headers=["*"],        # Permitir todos los encabezados
    expose_headers=["*"],       # Exponer todos los encabezados (opcional)
)

# ─── 2) Modelo de datos que recibirá el endpoint ───
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
    cv_filename: str

# ─── 3) Definición de la tabla “informes” (SQLAlchemy) ───
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

# ─── 4) Eventos de arranque y “shutdown” para conectar/desconectar la BD ───
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ─── 5) Endpoint para generar el informe ───
@app.post("/api/generar-informe")
async def generar_informe_endpoint(datos: DatosInforme):
    datos_dict = datos.dict()

    # ─ Construimos la variable `perfil` usando todo lo que viene en el body ─
    perfil = f"""
Nombre: {datos_dict.get('nombre', '')} {datos_dict.get('apellidos', '')}
Email: {datos_dict.get('email', '')}
WhatsApp: {datos_dict.get('whatsapp', '')}
Discapacidad: {datos_dict.get('discapacidad', '')}
Modalidad: {datos_dict.get('tipo', '')}
Puesto deseado: {datos_dict.get('puesto', '')}
Jornada: {datos_dict.get('jornada', '')}
Disponibilidad: {datos_dict.get('disponibilidad', '')}
Traslado: {datos_dict.get('traslado', '')}
CV: {datos_dict.get('cv_filename', '')}

Resultados de habilidades blandas:
- Toma de decisiones: {datos_dict.get('minijuego_decisiones_score', '')}
- Resolución de problemas: {datos_dict.get('minijuego_resolucion_score', '')}
- Comunicación: {datos_dict.get('minijuego_comunicacion_score', '')}
- Adaptabilidad: {datos_dict.get('minijuego_adaptabilidad_score', '')}
- Gestión del tiempo: {datos_dict.get('minijuego_tiempo_score', '')}
- Trabajo en equipo: {datos_dict.get('minijuego_equipo_score', '')}
- Creatividad: {datos_dict.get('minijuego_creatividad_score', '')}
- Liderazgo: {datos_dict.get('minijuego_liderazgo_score', '')}
- Pensamiento crítico: {datos_dict.get('minijuego_pensamiento_score', '')}
- Inteligencia emocional: {datos_dict.get('minijuego_emocional_score', '')}
"""

    # ─ Llamamos a la IA para que nos devuelva todo el texto estructurado ─
    texto_completo = generar_informe_ia(perfil)

    # ── 6) A partir del texto completo que devuelve la IA, extraemos cada sección ──
    #    (Esta lógica puedes modificarla si tu IA devuelve un formato distinto)
    resumen = ""
    fortalezas = []
    mejoras = []
    orientacion = ""
    conclusion = ""

    # Suponemos que la IA separa secciones con encabezados tipo “1. RESUMEN PERSONAL”, “2. FORTALEZAS”, etc.
    # Aquí hacemos un parse muy simple: buscamos líneas que empiecen con “- ” o “• ” para fortalezas/mejoras,
    # y buscamos palabras clave en minúsculas para orientacion y conclusion.
    for linea in texto_completo.splitlines():
        linea_limpia = linea.strip()
        if not linea_limpia:
            continue

        if linea_limpia.lower().startswith("1."):
            # A veces el “1.” se combina con el texto, ignoramos la etiqueta
            resumen = linea_limpia.split("1.", 1)[-1].strip()
        elif linea_limpia.startswith("-") or linea_limpia.startswith("•"):
            # Si la línea contiene “fortaleza” o “habilidad” la metemos en fortalezas
            if "fortaleza" in linea_limpia.lower() or "habilidad" in linea_limpia.lower():
                fortalezas.append(linea_limpia.lstrip("-• ").strip())
            elif "mejora" in linea_limpia.lower() or "oportunidad" in linea_limpia.lower():
                mejoras.append(linea_limpia.lstrip("-• ").strip())
        elif "orientación" in linea_limpia.lower():
            orientacion = linea_limpia
        elif "conclusión" in linea_limpia.lower():
            conclusion = linea_limpia

    # ── 7) Creamos el diccionario final “informe” que devolvemos al frontend ──
    informe = {
        "nombre": datos_dict.get("nombre", ""),
        "apellidos": datos_dict.get("apellidos", ""),
        "email": datos_dict.get("email", ""),
        "whatsapp": datos_dict.get("whatsapp", ""),
        "resumen": resumen,
        "fortalezas": fortalezas,
        "areas_mejora": mejoras,
        "orientacion": orientacion,
        "conclusion": conclusion,
    }

    # ── 8) Guardamos en la base de datos la fila nueva en la tabla “informes” ──
    query = informes.insert().values(
        nombre=informe["nombre"],
        apellidos=informe["apellidos"],
        email=informe["email"],
        whatsapp=informe["whatsapp"],
        resumen=informe["resumen"],
        fortalezas=", ".join(informe["fortalezas"]),
        areas_mejora=", ".join(informe["areas_mejora"]),
        orientacion=informe["orientacion"],
        conclusion=informe["conclusion"],
    )
    await database.execute(query)

    # ── 9) Devolvemos el JSON con “informe” al frontend ──
    return JSONResponse(content={"informe": informe})

# ─── 10) Para arrancar localmente con Python ───
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
