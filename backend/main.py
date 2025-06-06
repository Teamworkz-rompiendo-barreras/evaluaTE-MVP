# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sqlalchemy
from typing import List

from db import database
from generate_report import generar_informe as generar_informe_ia

app = FastAPI()

# Habilitar CORS para permitir llamadas desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Permite orígenes desde cualquier host
    allow_credentials=True,
    allow_methods=["*"],        # Permite todos los métodos HTTP (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],        # Permite todos los encabezados
    expose_headers=["*"],       # Expone todos los encabezados en la respuesta (opcional)
)

# ====================== MODELO Pydantic ======================
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
    minijuego_gestion_tiempo_score: str = ""
    minijuego_trabajo_equipo_score: str = ""
    minijuego_creatividad_score: str = ""
    minijuego_liderazgo_score: str = ""
    minijuego_pensamiento_score: str = ""
    minijuego_emocional_score: str = ""
    cv_filename: str

# ====================== DEFINICIÓN DE TABLA SQL ======================
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
    sqlalchemy.Column("minijuego_gestion_tiempo_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_trabajo_equipo_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_creatividad_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_liderazgo_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_pensamiento_score", sqlalchemy.Text),
    sqlalchemy.Column("minijuego_emocional_score", sqlalchemy.Text),
    sqlalchemy.Column("cv_filename", sqlalchemy.Text),
    sqlalchemy.Column("resumen", sqlalchemy.Text),
    sqlalchemy.Column("fortalezas", sqlalchemy.Text),
    sqlalchemy.Column("areas_mejora", sqlalchemy.Text),
    sqlalchemy.Column("orientacion", sqlalchemy.Text),
    sqlalchemy.Column("conclusion", sqlalchemy.Text),
)

# ====================== EVENTOS STARTUP / SHUTDOWN ======================
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ====================== ENDPOINT PRINCIPAL ======================
@app.post("/api/generar-informe")
async def generar_informe_endpoint(datos: DatosInforme):
    datos_dict = datos.dict()

    # 1) Construir un texto “perfil” para enviar a la IA (una sola cadena)
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
- Gestión del tiempo: {datos_dict['minijuego_gestion_tiempo_score']}
- Trabajo en equipo: {datos_dict['minijuego_trabajo_equipo_score']}
- Creatividad: {datos_dict['minijuego_creatividad_score']}
- Liderazgo: {datos_dict['minijuego_liderazgo_score']}
- Pensamiento crítico: {datos_dict['minijuego_pensamiento_score']}
- Inteligencia emocional: {datos_dict['minijuego_emocional_score']}
"""

    # 2) Llamamos a la función que invoca a Azure OpenAI para generar el texto completo del informe
    texto_completo = generar_informe_ia(perfil)

    # 3) Procesamos el texto completo para extraer las partes:
    #    - Un “resumen” (todo lo que venga antes de "2. FORTALEZAS")
    #    - Fortalezas, Mejora, Orientación, Conclusión
    resumen = ""
    fortalezas: List[str] = []
    mejoras: List[str] = []
    orientacion = ""
    conclusion = ""

    # Partimos el texto en líneas para analizar
    lineas = texto_completo.splitlines()
    # Buscamos dónde comienza “2.” o “FORTALEZAS” para separar el primer bloque como resumen
    linea_inicio_fort = 0
    for i, linea in enumerate(lineas):
        if linea.strip().lower().startswith("2") or linea.strip().lower().startswith("fortalezas"):
            linea_inicio_fort = i
            break

    # El “resumen” será todo lo que esté antes de esa línea
    resumen = "\n".join(lineas[:linea_inicio_fort]).strip()

    # Ahora buscamos en las líneas las viñetas de fortalezas y de mejoras.
    for linea in lineas[linea_inicio_fort:]:
        texto = linea.strip()
        if texto.startswith("-") or texto.startswith("•"):
            # Si la línea menciona “fortaleza” o “habilidad”, la agregamos a la lista de fortalezas
            if "fortaleza" in texto.lower() or "habilidad" in texto.lower():
                fortalezas.append(texto.lstrip("-• ").strip())
            # Si menciona “mejora” u “oportunidad”, la agregamos a mejoras
            elif "mejora" in texto.lower() or "oportunidad" in texto.lower():
                mejoras.append(texto.lstrip("-• ").strip())
        # Si la línea contiene “orientación”, la tomamos como orientación
        elif "orientación" in texto.lower():
            orientacion = texto
        # Si la línea contiene “conclusión”, la tomamos como conclusión
        elif "conclusión" in texto.lower():
            conclusion = texto

    # 4) Construimos el objeto Python para devolver al frontend
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
        "minijuego_gestion_tiempo_score": datos_dict["minijuego_gestion_tiempo_score"],
        "minijuego_trabajo_equipo_score": datos_dict["minijuego_trabajo_equipo_score"],
        "minijuego_creatividad_score": datos_dict["minijuego_creatividad_score"],
        "minijuego_liderazgo_score": datos_dict["minijuego_liderazgo_score"],
        "minijuego_pensamiento_score": datos_dict["minijuego_pensamiento_score"],
        "minijuego_emocional_score": datos_dict["minijuego_emocional_score"],
        "cv_filename": datos_dict["cv_filename"],
        "resumen": resumen,
        "fortalezas": fortalezas,
        "areas_mejora": mejoras,
        "orientacion": orientacion,
        "conclusion": conclusion,
    }

    # 5) Guardar en la base de datos
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
        minijuego_gestion_tiempo_score=informe["minijuego_gestion_tiempo_score"],
        minijuego_trabajo_equipo_score=informe["minijuego_trabajo_equipo_score"],
        minijuego_creatividad_score=informe["minijuego_creatividad_score"],
        minijuego_liderazgo_score=informe["minijuego_liderazgo_score"],
        minijuego_pensamiento_score=informe["minijuego_pensamiento_score"],
        minijuego_emocional_score=informe["minijuego_emocional_score"],
        cv_filename=informe["cv_filename"],
        resumen=informe["resumen"],
        fortalezas=", ".join(informe["fortalezas"]),
        areas_mejora=", ".join(informe["areas_mejora"]),
        orientacion=informe["orientacion"],
        conclusion=informe["conclusion"],
    )
    await database.execute(query)

    # 6) Finalmente devolvemos el JSON de respuesta al frontend
    return JSONResponse(content={"informe": informe})


# Si se ejecuta directamente con `python main.py`, arranca uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
