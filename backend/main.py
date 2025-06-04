# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sqlalchemy

from db import database
from generate_report import generar_informe as generar_informe_ia

app = FastAPI()

# Permitir CORS desde cualquier origen (para que tu Azure Static App pueda llamar al backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1) Modelo de entrada (añadimos todos los campos que tienes en la tabla y en el formulario)
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

# 2) Definición de la tabla "informes" en SQLAlchemy, con todas las columnas
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

@app.on_event("startup")
async def startup():
    # Conectar a la DB al arrancar la app
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    # Desconectar al cerrar
    await database.disconnect()

@app.post("/api/generar-informe")
async def generar_informe_endpoint(datos: DatosInforme):
    datos_dict = datos.dict()

    # Construir un perfil de ejemplo para enviarle al modelo de IA
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
CV: {datos_dict['cv_filename']}

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

    # Llamada al microservicio de IA que genera el texto completo del informe
    texto_completo = generar_informe_ia(perfil)

    # Intentamos extraer cada sección del texto que devuelve la IA
    # (Ajusta este parseo según el formato exacto que devuelva OpenAI)
    resumen = ""
    fortalezas = []
    mejoras = []
    orientacion = ""
    conclusion = ""

    # Supongamos que la IA retorna algo así:
    # 1. RESUMEN PERSONAL
    #    “… texto resumen …”
    # 2. FORTALEZAS
    #    “- Fortaleza 1
    #     - Fortaleza 2”
    # 3. OPORTUNIDADES DE MEJORA
    #    “- Mejora 1
    #     - Mejora 2”
    # 4. ORIENTACIÓN LABORAL PERSONALIZADA
    #    “… texto orientacion …”
    # 5. CONCLUSIÓN POSITIVA
    #    “… texto conclusión …”
    #
    # Ajusta esta lógica de división/“split” si tu prompt produce otro formato.

    lineas = [l.strip() for l in texto_completo.splitlines() if l.strip()]
    sección_actual = None
    for l in lineas:
        if l.lower().startswith("1.") or l.lower().startswith("resumen"):
            sección_actual = "resumen"
            continue
        if l.lower().startswith("2.") or l.lower().startswith("fortalezas"):
            sección_actual = "fortalezas"
            continue
        if l.lower().startswith("3.") or l.lower().startswith("oportunidades"):
            sección_actual = "mejoras"
            continue
        if l.lower().startswith("4.") or "orientacio" in l.lower():
            sección_actual = "orientacion"
            continue
        if l.lower().startswith("5.") or "conclusi" in l.lower():
            sección_actual = "conclusion"
            continue

        # Según la sección elegimos a qué lista/variable añadir la línea
        if sección_actual == "resumen":
            resumen += l + "\n"
        elif sección_actual == "fortalezas":
            if l.startswith("-") or l.startswith("•"):
                fortalezas.append(l.lstrip("-• ").strip())
        elif sección_actual == "mejoras":
            if l.startswith("-") or l.startswith("•"):
                mejoras.append(l.lstrip("-• ").strip())
        elif sección_actual == "orientacion":
            orientacion += l + "\n"
        elif sección_actual == "conclusion":
            conclusion += l + "\n"

    informe = {
        "nombre": datos_dict["nombre"],
        "apellidos": datos_dict["apellidos"],
        "email": datos_dict["email"],
        "whatsapp": datos_dict["whatsapp"],
        "discapacidad": datos_dict["discapacidad"],
        "tipo": datos_dict["tipo"],
        "puesto": datos_dict["puesto"],
        "jornada": datos_dict["jornada"],
        "disponibilidad": datos_dict["disponibilidad"],
        "traslado": datos_dict["traslado"],
        "minijuego_decisiones_score": datos_dict["minijuego_decisiones_score"],
        "minijuego_resolucion_score": datos_dict["minijuego_resolucion_score"],
        "minijuego_comunicacion_score": datos_dict["minijuego_comunicacion_score"],
        "minijuego_adaptabilidad_score": datos_dict["minijuego_adaptabilidad_score"],
        "minijuego_tiempo_score": datos_dict["minijuego_tiempo_score"],
        "minijuego_equipo_score": datos_dict["minijuego_equipo_score"],
        "minijuego_creatividad_score": datos_dict["minijuego_creatividad_score"],
        "minijuego_liderazgo_score": datos_dict["minijuego_liderazgo_score"],
        "minijuego_pensamiento_score": datos_dict["minijuego_pensamiento_score"],
        "minijuego_emocional_score": datos_dict["minijuego_emocional_score"],
        "resumen": resumen.strip(),
        "fortalezas": fortalezas,
        "areas_mejora": mejoras,
        "orientacion": orientacion.strip(),
        "conclusion": conclusion.strip()
    }

    # 3) Construir el INSERT con exactamente las mismas columnas que tu tabla
    query = informes.insert().values(
        nombre=informe["nombre"],
        apellidos=informe["apellidos"],
        email=informe["email"],
        whatsapp=informe["whatsapp"],
        discapacidad=informe["discapacidad"],
        tipo=informe["tipo"],
        puesto=informe["puesto"],
        jornada=informe["jornada"],
        disponibilidad=informe["disponibilidad"],
        traslado=informe["traslado"],
        minijuego_decisiones_score=informe["minijuego_decisiones_score"],
        minijuego_resolucion_score=informe["minijuego_resolucion_score"],
        minijuego_comunicacion_score=informe["minijuego_comunicacion_score"],
        minijuego_adaptabilidad_score=informe["minijuego_adaptabilidad_score"],
        minijuego_tiempo_score=informe["minijuego_tiempo_score"],
        minijuego_equipo_score=informe["minijuego_equipo_score"],
        minijuego_creatividad_score=informe["minijuego_creatividad_score"],
        minijuego_liderazgo_score=informe["minijuego_liderazgo_score"],
        minijuego_pensamiento_score=informe["minijuego_pensamiento_score"],
        minijuego_emocional_score=informe["minijuego_emocional_score"],
        resumen=informe["resumen"],
        fortalezas=", ".join(informe["fortalezas"]),
        areas_mejora=", ".join(informe["areas_mejora"]),
        orientacion=informe["orientacion"],
        conclusion=informe["conclusion"],
    )
    await database.execute(query)

    return JSONResponse(content={"informe": informe})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
