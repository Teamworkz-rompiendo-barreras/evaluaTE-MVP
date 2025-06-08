# backend/main.py

import os
import shutil 
from dotenv import load_dotenv   # <<< <-- Asegúrate de importarlo
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import status
from pydantic import BaseModel
import uvicorn
import sqlalchemy
import PyPDF2

from db import database, informes
from generate_report import generar_informe as generar_informe_ia

# ─── 1) Cargamos el .env antes de leer cualquier variable ───
load_dotenv()   # <<< Esto lee el archivo .env y pone las variables en el entorno

# ─── 2) Creamos la app y habilitamos CORS ───
app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# … resto de tu código en main.py …

# ─────────────────────────────────────────────────────────────────────────────
# 2) Modelo de datos para /api/generar-informe (Pydantic)
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
    cv_text: str                             # Ahora recibimos el texto completo del CV
    decision_score: int
    resolucion_score: int
    comunicacion_score: int
    adaptabilidad_score: int
    tiempo_score: int
    equipo_score: int
    creatividad_score: int
    liderazgo_score: int
    pensamiento_score: int
    emocional_score: int

# ─────────────────────────────────────────────────────────────────────────────
# 3) Al iniciar/conectar y al cerrar/desconectar la base de datos
@app.on_event("startup")
async def startup():
    await database.connect()
    # Si la carpeta uploads no existe, la creamos
    os.makedirs("uploads", exist_ok=True)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ─────────────────────────────────────────────────────────────────────────────
# 4) Endpoint para recibir el PDF de CV y extraer su texto
@app.post("/api/subir-cv")
async def subir_cv(file: UploadFile = File(...)):
    """
    Este endpoint recibe un archivo PDF, lo guarda en /uploads,
    extrae el texto con PyPDF2 y devuelve JSON con { "cv_text": "...texto completo..." }.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    # Guardar temporalmente el PDF
    upload_path = os.path.join("uploads", file.filename)
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extraer texto con PyPDF2
    try:
        reader = PyPDF2.PdfReader(upload_path)
        texto_extraido = ""
        for page in reader.pages:
            texto_extraido += page.extract_text() or ""
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extrayendo texto del PDF: {e}")

    # Opcionalmente podemos borrar el archivo PDF físico tras extraer el texto:
    # os.remove(upload_path)

    return {"cv_text": texto_extraido}


# ─────────────────────────────────────────────────────────────────────────────
# 5) Endpoint principal: generar el informe
@app.post("/api/generar-informe")
async def generar_informe_endpoint(datos: DatosInforme):
    datos_dict = datos.dict()

    # ─ Construir un “perfil” concatenando todas las partes (formulario + scores + cv_text)
    perfil = (
        f"Nombre: {datos_dict['nombre']} {datos_dict['apellidos']}\n"
        f"Email: {datos_dict['email']}\n"
        f"WhatsApp: {datos_dict['whatsapp']}\n"
        f"Discapacidad: {datos_dict['discapacidad']}\n"
        f"Modalidad: {datos_dict['tipo']}\n"
        f"Puesto deseado: {datos_dict['puesto']}\n"
        f"Jornada: {datos_dict['jornada']}\n"
        f"Disponibilidad: {datos_dict['disponibilidad']}\n"
        f"Traslado: {datos_dict['traslado']}\n\n"
        f"--- TEXTO COMPLETO DEL CV ---\n{datos_dict['cv_text']}\n\n"
        f"--- RESULTADOS DE SOFT SKILLS ---\n"
        f"- Toma de decisiones: {datos_dict['decision_score']}\n"
        f"- Resolución de problemas: {datos_dict['resolucion_score']}\n"
        f"- Comunicación: {datos_dict['comunicacion_score']}\n"
        f"- Adaptabilidad: {datos_dict['adaptabilidad_score']}\n"
        f"- Gestión del tiempo: {datos_dict['tiempo_score']}\n"
        f"- Trabajo en equipo: {datos_dict['equipo_score']}\n"
        f"- Creatividad: {datos_dict['creatividad_score']}\n"
        f"- Liderazgo: {datos_dict['liderazgo_score']}\n"
        f"- Pensamiento crítico: {datos_dict['pensamiento_score']}\n"
        f"- Inteligencia emocional: {datos_dict['emocional_score']}\n"
    )

    # ─ Llamamos a la IA para que genere el informe completo
    try:
        texto_completo = generar_informe_ia(perfil)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando informe con IA: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # 6) Parsear las 5 secciones del texto completo de la IA
    resumen = ""
    fortalezas = []
    mejoras = []
    orientacion = ""
    conclusion = ""

    for linea in texto_completo.splitlines():
        linea_limpia = linea.strip()
        if not linea_limpia:
            continue

        # Detectar la sección “1. RESUMEN PERSONAL”
        if linea_limpia.lower().startswith("1.") and "resumen" in linea_limpia.lower():
            # Tomamos todo después de "1."
            resumen = linea_limpia.split("1.", 1)[-1].strip()
            continue

        # Listas de fortalezas/áreas de mejora con guión
        if linea_limpia.startswith("-") or linea_limpia.startswith("•"):
            texto_item = linea_limpia.lstrip("-• ").strip()
            if "fortaleza" in texto_item.lower() or "habilidad" in texto_item.lower():
                fortalezas.append(texto_item)
            elif "mejora" in texto_item.lower() or "oportunidad" in texto_item.lower():
                mejoras.append(texto_item)
            continue

        # Detección de la sección “4. ORIENTACIÓN LABORAL”
        if "orientación" in linea_limpia.lower():
            orientacion = linea_limpia
            continue

        # Detección de la sección “5. CONCLUSIÓN”
        if "conclusión" in linea_limpia.lower():
            conclusion = linea_limpia
            continue

    # Si alguna sección quedara vacía, la IA pudo no haberla etiquetado exactamente. 
    # Podríamos fallback a buscarlas por número (“2.”, “3.”), pero asumimos que la IA sigue la 
    # instrucción de “1.”, “2.”, etc.

    # ─────────────────────────────────────────────────────────────────────────
    # 7) Insertar fila en la tabla `informes`
    query = informes.insert().values(
        nombre = datos_dict["nombre"],
        apellidos = datos_dict["apellidos"],
        email = datos_dict["email"],
        whatsapp = datos_dict["whatsapp"],
        discapacidad = datos_dict["discapacidad"],
        tipo = datos_dict["tipo"],
        puesto = datos_dict["puesto"],
        jornada = datos_dict["jornada"],
        disponibilidad = datos_dict["disponibilidad"],
        traslado = datos_dict["traslado"],
        cv_text = datos_dict["cv_text"],
        decision_score = datos_dict["decision_score"],
        resolucion_score = datos_dict["resolucion_score"],
        comunicacion_score = datos_dict["comunicacion_score"],
        adaptabilidad_score = datos_dict["adaptabilidad_score"],
        tiempo_score = datos_dict["tiempo_score"],
        equipo_score = datos_dict["equipo_score"],
        creatividad_score = datos_dict["creatividad_score"],
        liderazgo_score = datos_dict["liderazgo_score"],
        pensamiento_score = datos_dict["pensamiento_score"],
        emocional_score = datos_dict["emocional_score"],
        resumen = resumen,
        fortalezas = " | ".join(fortalezas),
        areas_mejora = " | ".join(mejoras),
        orientacion = orientacion,
        conclusion = conclusion
    )
    try:
        await database.execute(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando en la base de datos: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # 8) Devolver JSON con el informe parseado + scores
    return JSONResponse(content={
        "informe": {
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
            "scores": {
                "Toma de decisiones": datos_dict["decision_score"],
                "Resolución de problemas": datos_dict["resolucion_score"],
                "Comunicación": datos_dict["comunicacion_score"],
                "Adaptabilidad": datos_dict["adaptabilidad_score"],
                "Gestión del tiempo": datos_dict["tiempo_score"],
                "Trabajo en equipo": datos_dict["equipo_score"],
                "Creatividad": datos_dict["creatividad_score"],
                "Liderazgo": datos_dict["liderazgo_score"],
                "Pensamiento crítico": datos_dict["pensamiento_score"],
                "Inteligencia emocional": datos_dict["emocional_score"]
            },
            "resumen": resumen,
            "fortalezas": fortalezas,
            "areas_mejora": mejoras,
            "orientacion": orientacion,
            "conclusion": conclusion
        }
    })


# ─────────────────────────────────────────────────────────────────────────────
# 9) Si ejecutamos “python main.py”, arrancamos Uvicorn en local
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
