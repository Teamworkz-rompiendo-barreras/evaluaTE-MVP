# backend/main.py

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn
from typing import List, Optional, Dict, Any
from datetime import datetime
import io
import json
from pypdf import PdfReader
import os
import openai
from openai import AzureOpenAI
from dotenv import load_dotenv
import logging
import tempfile
from feedback_notifications import feedback_notifier

# Importar la función de generación de informe profesional
from generate_report import generar_informe

# Importar las funciones de análisis de CV
from cv_analyzer import extract_pdf_info

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def extract_basic_cv_info(text: str) -> dict:
    """Extrae información básica del texto del CV cuando no hay datos estructurados"""
    info = {
        "strengths": [],
        "weaknesses": [],
        "feedback": "Análisis básico del CV basado en el texto extraído",
        "structure": "Información extraída del CV",
        "coherence": "Datos disponibles del CV",
        "experience": "",
        "skills": [],
        "education": [],
        "alerts": []
    }
    
    # Buscar patrones básicos en el texto
    lines = text.split('\n')
    
    # Buscar habilidades técnicas comunes
    tech_keywords = [
        "javascript", "python", "java", "c++", "c#", "php", "ruby", "go", "rust",
        "react", "angular", "vue", "node.js", "express", "django", "flask",
        "sql", "mysql", "postgresql", "mongodb", "redis",
        "html", "css", "bootstrap", "tailwind", "sass", "less",
        "git", "docker", "kubernetes", "aws", "azure", "gcp",
        "machine learning", "ai", "data science", "analytics"
    ]
    
    found_skills = []
    for line in lines:
        line_lower = line.lower()
        for keyword in tech_keywords:
            if keyword in line_lower:
                found_skills.append(keyword.title())
    
    info["skills"] = list(set(found_skills))  # Eliminar duplicados
    
    # Buscar formación académica
    education_keywords = ["universidad", "universidad", "grado", "licenciatura", "ingeniería", "master", "máster", "doctorado", "curso", "certificación"]
    found_education = []
    for line in lines:
        line_lower = line.lower()
        for keyword in education_keywords:
            if keyword in line_lower:
                found_education.append(line.strip())
    
    info["education"] = found_education[:5]  # Limitar a 5 elementos
    
    # Buscar experiencia laboral
    experience_keywords = ["años", "experiencia", "desarrollador", "programador", "analista", "ingeniero", "consultor"]
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in experience_keywords):
            info["experience"] = line.strip()
            break
    
    # Si no se encontró experiencia específica, usar el texto completo como experiencia
    if not info["experience"] and text.strip():
        info["experience"] = text[:200] + "..." if len(text) > 200 else text
    
    return info

def format_cv_analysis(cv_data: dict) -> str:
    """Formatea el análisis del CV de manera legible para la IA"""
    if not cv_data:
        return "No se proporcionó análisis de CV"
    
    # Verificar si cv_data es un diccionario válido
    if not isinstance(cv_data, dict):
        return "Formato de análisis de CV inválido"
    
    formatted = []
    
    # Siempre incluir información disponible, incluso si está incompleta
    if cv_data.get('strengths'):
        formatted.append("PUNTOS FUERTES:")
        for strength in cv_data['strengths']:
            formatted.append(f"  • {strength}")
        formatted.append("")
    elif cv_data.get('experience'):
        formatted.append("EXPERIENCIA LABORAL:")
        formatted.append(f"  • {cv_data['experience']}")
        formatted.append("")
    
    if cv_data.get('weaknesses'):
        formatted.append("ÁREAS DE MEJORA:")
        for weakness in cv_data['weaknesses']:
            formatted.append(f"  • {weakness}")
        formatted.append("")
    
    if cv_data.get('feedback'):
        formatted.append(f"FEEDBACK GENERAL: {cv_data['feedback']}")
        formatted.append("")
    
    if cv_data.get('structure'):
        formatted.append(f"ESTRUCTURA: {cv_data['structure']}")
        formatted.append("")
    
    if cv_data.get('coherence'):
        formatted.append(f"COHERENCIA: {cv_data['coherence']}")
        formatted.append("")
    
    if cv_data.get('experience'):
        formatted.append(f"EXPERIENCIA LABORAL: {cv_data['experience']}")
        formatted.append("")
    
    if cv_data.get('skills'):
        formatted.append("HABILIDADES TÉCNICAS DETECTADAS:")
        for skill in cv_data['skills']:
            formatted.append(f"  • {skill}")
        formatted.append("")
    
    if cv_data.get('education'):
        formatted.append("FORMACIÓN DETECTADA:")
        for edu in cv_data['education']:
            formatted.append(f"  • {edu}")
        formatted.append("")
    
    if cv_data.get('alerts'):
        formatted.append("ALERTAS O PUNTOS CRÍTICOS:")
        for alert in cv_data['alerts']:
            formatted.append(f"  ⚠️ {alert}")
        formatted.append("")
    
    # Si no hay datos estructurados pero hay texto raw, incluirlo
    if not formatted and cv_data.get('raw_text'):
        formatted.append("CONTENIDO DEL CV:")
        formatted.append(cv_data['raw_text'][:1000] + "..." if len(cv_data['raw_text']) > 1000 else cv_data['raw_text'])
        formatted.append("")
    
    # Si no hay ningún dato estructurado, intentar extraer información básica
    if not formatted:
        # Buscar cualquier campo que contenga información
        for key, value in cv_data.items():
            if value and key not in ['raw_text', 'analysis']:
                if isinstance(value, list) and value:
                    formatted.append(f"{key.upper()}:")
                    for item in value[:5]:  # Limitar a 5 elementos
                        formatted.append(f"  • {item}")
                    formatted.append("")
                elif isinstance(value, str) and value.strip():
                    formatted.append(f"{key.upper()}: {value}")
                    formatted.append("")
    
    return "\n".join(formatted) if formatted else "Análisis de CV disponible pero sin detalles específicos. Se realizará la evaluación basada en las habilidades soft evaluadas."

def format_job_preferences(preferences: dict) -> str:
    """Formatea las preferencias laborales de manera legible para la IA"""
    if not preferences:
        return "No se especificaron preferencias laborales"
    
    formatted = []
    
    if preferences.get('areas'):
        formatted.append("ÁREAS DE INTERÉS:")
        for area in preferences['areas']:
            formatted.append(f"  • {area}")
        formatted.append("")
    
    if preferences.get('needs'):
        formatted.append("NECESIDADES ESPECÍFICAS:")
        for need in preferences['needs']:
            formatted.append(f"  • {need}")
        formatted.append("")
    
    if preferences.get('workMode'):
        formatted.append(f"MODO DE TRABAJO: {preferences['workMode']}")
    
    if preferences.get('availability'):
        formatted.append(f"DISPONIBILIDAD: {preferences['availability']}")
    
    if preferences.get('willingToRelocate'):
        formatted.append(f"DISPONIBILIDAD DE REUBICACIÓN: {'Sí' if preferences['willingToRelocate'] else 'No'}")
    
    if preferences.get('hasDisabilityCert'):
        formatted.append(f"CERTIFICADO DE DISCAPACIDAD: {'Sí' if preferences['hasDisabilityCert'] else 'No'}")
    
    return "\n".join(formatted) if formatted else "Preferencias laborales básicas especificadas"

# Validación de variables de entorno críticas
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Validar configuración crítica
if not all([API_KEY, ENDPOINT, DEPLOYMENT, API_VERSION]):
    logger.warning("⚠️ Variables de entorno de Azure OpenAI incompletas. Algunas funciones pueden no estar disponibles.")
    logger.warning(f"API_KEY: {'✅' if API_KEY else '❌'}")
    logger.warning(f"ENDPOINT: {'✅' if ENDPOINT else '❌'}")
    logger.warning(f"DEPLOYMENT: {'✅' if DEPLOYMENT else '❌'}")
    logger.warning(f"API_VERSION: {'✅' if API_VERSION else '❌'}")
    logger.warning("💡 Para habilitar análisis completo de CV, configura las variables de entorno de Azure OpenAI")

# Crear cliente solo si todas las variables están disponibles
if all([API_KEY, ENDPOINT, DEPLOYMENT, API_VERSION]) and API_KEY and ENDPOINT and DEPLOYMENT and API_VERSION:
    client = AzureOpenAI(api_key=API_KEY, api_version=API_VERSION, azure_endpoint=ENDPOINT)
else:
    client = None

# Tipos compartidos – puedes moverlos a un paquete común si lo usas también en frontend
class SoftSkillResult(BaseModel):
    skill: str
    score: int
    level: str  # 'bajo', 'medio', 'alto'
    confidence: int

class CvAnalysis(BaseModel):
    strengths: List[str] = Field(description="Puntos fuertes del CV")
    weaknesses: List[str] = Field(description="Áreas de mejora del CV")
    feedback: Optional[str] = Field(None, description="Feedback general sobre el CV")
    structure: Optional[str] = Field(None, description="Análisis de la estructura del CV")
    coherence: Optional[str] = Field(None, description="Análisis de la coherencia del CV")
    experience: Optional[str] = Field(None, description="Análisis de la experiencia laboral")
    skills: Optional[List[str]] = Field([], description="Habilidades técnicas detectadas")
    education: Optional[List[str]] = Field([], description="Formación detectada")
    alerts: Optional[List[str]] = Field([], description="Alertas o puntos críticos detectados")

class JobPreference(BaseModel):
    areas: List[str]
    needs: List[str]
    workMode: Optional[str] = "remoto"  # 'remoto', 'presencial', 'híbrido'
    availability: Optional[str] = "completa"  # 'mañana', 'tarde', 'completa'
    willingToRelocate: bool = False
    hasDisabilityCert: bool = False

class AccessibilitySettings(BaseModel):
    easyReadingMode: bool = False
    audioAssistiveMode: bool = False
    showPictograms: bool = False
    contrastLevel: str = "normal"  # 'normal', 'alto', 'muy-alto'

class GameDecisionLog(BaseModel):
    sceneId: int
    decisions: List[Dict[str, Any]]
    totalSteps: int
    totalTime: int
    averageConfidence: float
    emotionalTrend: List[str]
    accessibilityUsed: bool
    accessibilitySettings: Optional[AccessibilitySettings] = None

class EmployabilityReportRequest(BaseModel):
    userId: str
    fullName: str
    softSkills: List[SoftSkillResult]
    cvAnalysis: Optional[CvAnalysis] = None
    jobPreferences: Optional[JobPreference] = None
    completedGames: List[str] = []  # Cambiado de List[int] a List[str] para compatibilidad
    logs: List[GameDecisionLog] = []

class ReportResponse(BaseModel):
    report: Dict[str, Any]
    recommendations: Dict[str, List[str]]
    employabilityScore: int
    level: str
    summary: str
    createdAt: str

class FeedbackRequest(BaseModel):
    informe: str
    rating: str  # "Útil" o "No útil"
    comment: str
    userData: dict

app = FastAPI(title="EvaluaTE Backend", version="1.0.0")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Bienvenida/o a EvaluaTE MVP", "status": "running"}

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3005",
        "http://localhost:3006",
        "http://localhost:5173",
        "https://yellow-mud-0b6281c1e.6.azurestaticapps.net",
        "https://*.azurestaticapps.net",
        "https://*.azurewebsites.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/logs/scene", response_model=Dict[str, Any])
async def log_scene_decision(data: Dict[str, Any]):
    """Guarda decisiones tomadas en cada escena"""
    print("LOG SCENE:", data)
    return {"success": True}

@app.post("/api/logs/game-complete", response_model=Dict[str, Any])
async def log_game_complete(data: Dict[str, Any]):
    """Guarda cuando se completa un juego"""
    print("GAME COMPLETE:", data)
    return {"success": True}

@app.post("/api/informe-ia", response_model=ReportResponse)
async def generate_ia_report(request: EmployabilityReportRequest):
    """
    Genera un informe de empleabilidad usando IA avanzada.
    """
    try:
        logger.info(f"🔄 Iniciando generación de informe profesional para: {request.fullName}")
        
        # Preparar perfil completo para la IA
        perfil_completo = {
            'datos_personales': {
                'nombre': request.fullName,
                'user_id': request.userId
            },
            'habilidades_soft': [
                {
                    'habilidad': skill.skill,
                    'nivel': skill.level,
                    'puntuacion': skill.score,
                    'confianza': skill.confidence
                }
                for skill in request.softSkills
            ],
            'analisis_cv': request.cvAnalysis.dict() if request.cvAnalysis else {},
            'preferencias_laborales': request.jobPreferences.dict() if request.jobPreferences else {},
            'juegos_completados': request.completedGames,
            'logs_juegos': [log.dict() for log in request.logs] if request.logs else []
        }
        
        # Formatear el perfil como texto para la IA
        perfil_texto = f"""
DATOS DEL CANDIDATO:
Nombre: {request.fullName}
ID de Usuario: {request.userId}

HABILIDADES SOFT EVALUADAS:
{chr(10).join([f"- {skill.skill}: {skill.confidence}%" for skill in request.softSkills])}

ANÁLISIS DETALLADO DEL CV:
{format_cv_analysis(request.cvAnalysis.dict()) if request.cvAnalysis else "No se ha proporcionado análisis de CV."}

PREFERENCIAS LABORALES:
{format_job_preferences(request.jobPreferences.dict()) if request.jobPreferences else "No se han especificado preferencias laborales."}

JUEGOS COMPLETADOS:
{', '.join(perfil_completo['juegos_completados']) if perfil_completo['juegos_completados'] else "El candidato no ha completado juegos de evaluación. La evaluación se basa en las habilidades soft proporcionadas."}

LOGS DE JUEGOS:
{json.dumps(perfil_completo['logs_juegos'], indent=2, ensure_ascii=False) if perfil_completo['logs_juegos'] else "No se dispone de logs detallados de juegos. La evaluación se basa en los resultados de habilidades soft proporcionados."}
"""
        
        logger.info("🤖 Generando informe profesional con IA...")
        
        # Generar informe profesional usando IA
        informe_profesional = generar_informe(perfil_texto)
        
        logger.info("✅ Informe profesional generado exitosamente")
        
        # Calcular puntuación de empleabilidad basada en habilidades
        high_skills = [skill for skill in request.softSkills if skill.level.lower() == "alto"]
        medium_skills = [skill for skill in request.softSkills if skill.level.lower() == "medio"]
        low_skills = [skill for skill in request.softSkills if skill.level.lower() == "bajo"]
        
        score_high = len(high_skills) * 100
        score_medium = len(medium_skills) * 65
        score_low = len(low_skills) * 30
        total_score = (score_high + score_medium + score_low) // max(1, len(request.softSkills))
        
        # Nivel de empleabilidad
        level = (
            "Alta empleabilidad"
            if total_score >= 80
            else "Empleabilidad media"
            if total_score >= 50
            else "Baja empleabilidad"
        )
        
        # Extraer recomendaciones del informe de IA
        # Buscar secciones específicas en el informe
        recomendaciones = {
            "roles": [],
            "resources": ["Platzi", "Microsoft Learn"],
            "cvImprovements": [],
            "nextSteps": ["Revisar el informe completo", "Implementar las recomendaciones", "Seguir el plan de desarrollo"]
        }
        
        # Intentar extraer roles recomendados del informe
        if "puestos de trabajo recomendados" in informe_profesional.lower() or "empleos compatibles" in informe_profesional.lower():
            # Buscar patrones de roles en el texto
            import re
            roles_pattern = r"(?:puesto|rol|empleo|trabajo)[\s\w]*recomendado[^:]*:\s*([^.\n]+)"
            roles_matches = re.findall(roles_pattern, informe_profesional, re.IGNORECASE)
            if roles_matches:
                recomendaciones["roles"] = [rol.strip() for rol in roles_matches[:3]]
        
        # Si no se encontraron roles, usar algunos por defecto basados en habilidades
        if not recomendaciones["roles"]:
            if any(skill.level.lower() == "alto" for skill in request.softSkills):
                recomendaciones["roles"].extend(["Desarrollador frontend", "Soporte técnico"])
            if request.cvAnalysis and request.cvAnalysis.strengths:
                recomendaciones["roles"].append("Analista de datos")
        
        return {
            "report": {
                "userId": request.userId,
                "fullName": request.fullName,
                "softSkills": [
                    {**skill.dict(), "confidence": round(skill.confidence * 100)}
                    for skill in request.softSkills
                ],
                "employabilityScore": total_score,
                "jobPreferences": request.jobPreferences.dict() if request.jobPreferences else {},
                "cvAnalysis": request.cvAnalysis.dict() if request.cvAnalysis else None,
                "createdAt": datetime.now().isoformat(),
                "completedGames": request.completedGames,
                "level": level,
                "informeProfesional": informe_profesional  # Incluir el informe completo de IA
            },
            "recommendations": recomendaciones,
            "summary": f"{request.fullName}, tu informe profesional ha sido generado. Nivel de empleabilidad: {level}",
            "employabilityScore": total_score,
            "level": level,
            "createdAt": datetime.now().isoformat(),
        }

    except RuntimeError as e:
        # Error de configuración de Azure OpenAI
        logger.error(f"❌ Error de configuración Azure OpenAI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error de configuración de Azure OpenAI: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Error generando informe profesional: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error generando informe: {str(e)}"
        )

@app.get("/api/informe-ia")
async def get_ia_report():
    """Endpoint GET para el informe de IA"""
    return {"message": "Endpoint de informe de IA disponible"}

@app.post("/api/logs/report", response_model=ReportResponse)
async def generate_report(request: EmployabilityReportRequest):
    """Genera informe final profesional usando IA basado en datos del usuario"""

    try:
        logger.info(f"🔄 Iniciando generación de informe profesional para: {request.fullName}")
        
        # Preparar el perfil completo para el análisis de IA
        perfil_completo = {
            "datos_personales": {
                "nombre": request.fullName,
                "user_id": request.userId
            },
            "habilidades_soft": [
                {
                    "habilidad": skill.skill,
                    "puntuacion": skill.score,
                    "nivel": skill.level,
                    "confianza": skill.confidence
                }
                for skill in request.softSkills
            ],
            "analisis_cv": request.cvAnalysis.dict() if request.cvAnalysis else {},
            "preferencias_laborales": request.jobPreferences.dict() if request.jobPreferences else {},
            "juegos_completados": request.completedGames,
            "logs_juegos": [log.dict() for log in request.logs] if request.logs else []
        }
        
        # Convertir a formato de texto para la IA
        perfil_texto = f"""
PERFIL COMPLETO DEL CANDIDATO:

DATOS PERSONALES:
- Nombre: {perfil_completo['datos_personales']['nombre']}
- ID: {perfil_completo['datos_personales']['user_id']}

HABILIDADES SOFT EVALUADAS:
{chr(10).join([f"- {h['habilidad']}: {h['puntuacion']}% (Nivel: {h['nivel']}, Confianza: {h['confianza']}%)" for h in perfil_completo['habilidades_soft']])}

ANÁLISIS DETALLADO DEL CV:
{format_cv_analysis(perfil_completo['analisis_cv'])}

PREFERENCIAS LABORALES:
{format_job_preferences(perfil_completo['preferencias_laborales']) if perfil_completo['preferencias_laborales'] else "El candidato no ha especificado preferencias laborales detalladas. Se realizará la evaluación basada en las habilidades soft evaluadas."}

JUEGOS COMPLETADOS:
{', '.join(perfil_completo['juegos_completados']) if perfil_completo['juegos_completados'] else "El candidato no ha completado juegos de evaluación. La evaluación se basa en las habilidades soft proporcionadas."}

LOGS DE JUEGOS:
{json.dumps(perfil_completo['logs_juegos'], indent=2, ensure_ascii=False) if perfil_completo['logs_juegos'] else "No se dispone de logs detallados de juegos. La evaluación se basa en los resultados de habilidades soft proporcionados."}
"""
        
        logger.info("🤖 Generando informe profesional con IA...")
        
        # Generar informe profesional usando IA
        informe_profesional = generar_informe(perfil_texto)
        
        logger.info("✅ Informe profesional generado exitosamente")
        
        # Calcular puntuación de empleabilidad basada en habilidades
        high_skills = [skill for skill in request.softSkills if skill.level.lower() == "alto"]
        medium_skills = [skill for skill in request.softSkills if skill.level.lower() == "medio"]
        low_skills = [skill for skill in request.softSkills if skill.level.lower() == "bajo"]
        
        score_high = len(high_skills) * 100
        score_medium = len(medium_skills) * 65
        score_low = len(low_skills) * 30
        total_score = (score_high + score_medium + score_low) // max(1, len(request.softSkills))
        
        # Nivel de empleabilidad
        level = (
            "Alta empleabilidad"
            if total_score >= 80
            else "Empleabilidad media"
            if total_score >= 50
            else "Baja empleabilidad"
        )
        
        # Extraer recomendaciones del informe de IA
        # Buscar secciones específicas en el informe
        recomendaciones = {
            "roles": [],
            "resources": ["Platzi", "Microsoft Learn"],
            "cvImprovements": [],
            "nextSteps": ["Revisar el informe completo", "Implementar las recomendaciones", "Seguir el plan de desarrollo"]
        }
        
        # Intentar extraer roles recomendados del informe
        if "puestos de trabajo recomendados" in informe_profesional.lower() or "empleos compatibles" in informe_profesional.lower():
            # Buscar patrones de roles en el texto
            import re
            roles_pattern = r"(?:puesto|rol|empleo|trabajo)[\s\w]*recomendado[^:]*:\s*([^.\n]+)"
            roles_matches = re.findall(roles_pattern, informe_profesional, re.IGNORECASE)
            if roles_matches:
                recomendaciones["roles"] = [rol.strip() for rol in roles_matches[:3]]
        
        # Si no se encontraron roles, usar algunos por defecto basados en habilidades
        if not recomendaciones["roles"]:
            if any(skill.level.lower() == "alto" for skill in request.softSkills):
                recomendaciones["roles"].extend(["Desarrollador frontend", "Soporte técnico"])
            if request.cvAnalysis and request.cvAnalysis.strengths:
                recomendaciones["roles"].append("Analista de datos")
        
        return {
            "report": {
                "userId": request.userId,
                "fullName": request.fullName,
                "softSkills": [
                    {**skill.dict(), "confidence": round(skill.confidence * 100)}
                    for skill in request.softSkills
                ],
                "employabilityScore": total_score,
                "jobPreferences": request.jobPreferences.dict() if request.jobPreferences else {},
                "cvAnalysis": request.cvAnalysis.dict() if request.cvAnalysis else None,
                "createdAt": datetime.now().isoformat(),
                "completedGames": request.completedGames,
                "level": level,
                "informeProfesional": informe_profesional  # Incluir el informe completo de IA
            },
            "recommendations": recomendaciones,
            "summary": f"{request.fullName}, tu informe profesional ha sido generado. Nivel de empleabilidad: {level}",
            "employabilityScore": total_score,
            "level": level,
            "createdAt": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error generando informe profesional: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/api/informe-ia/feedback")
async def receive_feedback(request: FeedbackRequest):
    """
    Recibe feedback de los usuarios sobre los informes generados por la IA.
    Este feedback se guarda para mejorar futuros informes.
    """
    try:
        feedback_data = {
            "informe": request.informe,
            "rating": request.rating,
            "comment": request.comment,
            "userData": request.userData,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Guardar feedback en archivo JSON
        feedback_file = "feedback_ia.json"
        feedbacks = []
        
        # Leer feedback existente si existe
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    feedbacks = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                feedbacks = []
        
        # Agregar nuevo feedback
        feedbacks.append(feedback_data)
        
        # Guardar feedback actualizado
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Feedback guardado exitosamente. Rating: {request.rating}")
        
        # Enviar notificación por email (en segundo plano)
        try:
            feedback_notifier.send_feedback_notification(feedback_data)
        except Exception as e:
            logger.warning(f"⚠️ Error enviando notificación: {str(e)}")
        
        return {"success": True, "message": "Feedback recibido correctamente"}
        
    except Exception as e:
        logger.error(f"❌ Error guardando feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/informe-ia/feedback/stats")
async def get_feedback_stats():
    """
    Obtiene estadísticas del feedback recibido para análisis y mejora.
    """
    try:
        feedback_file = "feedback_ia.json"
        if not os.path.exists(feedback_file):
            return {
                "total_feedback": 0,
                "useful_feedback": 0,
                "not_useful_feedback": 0,
                "useful_percentage": 0,
                "recent_feedback": [],
                "common_comments": []
            }
        
        with open(feedback_file, 'r', encoding='utf-8') as f:
            feedbacks = json.load(f)
        
        total_feedback = len(feedbacks)
        useful_feedback = len([f for f in feedbacks if f.get('rating') == 'Útil'])
        not_useful_feedback = len([f for f in feedbacks if f.get('rating') == 'No útil'])
        useful_percentage = (useful_feedback / total_feedback * 100) if total_feedback > 0 else 0
        
        # Últimos 10 feedbacks
        recent_feedback = feedbacks[-10:] if len(feedbacks) > 10 else feedbacks
        
        # Comentarios más comunes (simplificado)
        comments = [f.get('comment', '').strip() for f in feedbacks if f.get('comment', '').strip()]
        common_comments = []
        if comments:
            # Tomar comentarios únicos que aparezcan más de una vez
            from collections import Counter
            comment_counts = Counter(comments)
            common_comments = [comment for comment, count in comment_counts.most_common(5) if count > 1]
        
        return {
            "total_feedback": total_feedback,
            "useful_feedback": useful_feedback,
            "not_useful_feedback": not_useful_feedback,
            "useful_percentage": round(useful_percentage, 2),
            "recent_feedback": recent_feedback,
            "common_comments": common_comments
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas de feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/pdf/analyze-cv", response_model=CvAnalysis)
async def analyze_cv(
    file: UploadFile = File(...),
    userId: str = Form(...),
    fullName: str = Form(...),
    softSkills: str = Form(...),  # JSON stringified array
    jobPreferences: str = Form(...),  # JSON stringified object
    completedGames: str = Form(...),  # JSON stringified array
):
    """
    Analiza un CV subido y devuelve un análisis estructurado usando IA avanzada.
    """
    try:
        logger.info(f"Iniciando análisis avanzado de CV para usuario {userId}")
        logger.info(f"Archivo recibido: {file.filename}, tamaño: {file.size} bytes")
        
        # Verificar que sea un PDF
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
        
        # Leer el contenido del archivo
        contents = await file.read()
        logger.info(f"Contenido leído: {len(contents)} bytes")
        
        # Verificar que sea un PDF válido
        try:
            pdf_reader = PdfReader(io.BytesIO(contents))
            if len(pdf_reader.pages) == 0:
                raise HTTPException(status_code=400, detail="El archivo PDF está vacío")
            logger.info(f"PDF válido con {len(pdf_reader.pages)} páginas")
        except Exception as e:
            logger.error(f"Error al validar PDF: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error al leer el PDF: {str(e)}")
        
        # Extraer información del PDF usando el nuevo cv_analyzer con IA
        logger.info("Iniciando análisis con cv_analyzer...")
        cv_result = extract_pdf_info(contents)
        
        if cv_result.get("error"):
            logger.error(f"Error en análisis de CV: {cv_result['error']}")
            # En lugar de fallar completamente, crear un análisis básico
            logger.info("Creando análisis básico como fallback...")
            
            # Intentar extraer texto básico del PDF
            try:
                pdf_reader = PdfReader(io.BytesIO(contents))
                basic_text = ""
                for page in pdf_reader.pages:
                    basic_text += page.extract_text() + "\n"
                
                if basic_text.strip():
                    # Crear análisis básico con el texto extraído
                    basic_analysis = extract_basic_cv_info(basic_text)
                    logger.info("Análisis básico creado exitosamente")
                    
                    return CvAnalysis(**basic_analysis)
                else:
                    raise HTTPException(status_code=400, detail=cv_result["error"])
            except Exception as basic_error:
                logger.error(f"Error en análisis básico: {str(basic_error)}")
                raise HTTPException(status_code=400, detail=cv_result["error"])
        
        # Obtener el análisis completo
        cv_analysis = cv_result.get("analysis", {})
        cv_info = cv_result.get("cv_info", {})
        full_cv_data = cv_result.get("full_cv_data", {})
        
        logger.info(f"Análisis obtenido: {len(cv_analysis)} elementos")
        logger.info(f"Datos completos extraídos: {len(full_cv_data)} secciones")
        
        # Verificar que tenemos un análisis válido
        if not cv_analysis or not all(key in cv_analysis for key in ["strengths", "weaknesses", "feedback"]):
            logger.warning("Análisis incompleto, generando análisis básico")
            
            # Crear análisis básico con los datos disponibles
            analysis_data = {
                "strengths": ["CV procesado correctamente"],
                "weaknesses": ["Análisis limitado por estructura del CV"],
                "feedback": "El CV ha sido procesado. Se recomienda revisar la información extraída.",
                "structure": "regular",
                "coherence": "regular",
                "experience": "limitada",
                "skills": cv_info.get("software", []),
                "education": cv_info.get("educacion", []),
                "alerts": ["Análisis automático - revisar información extraída"]
            }
        else:
            # Usar el análisis completo del cv_analyzer
            logger.info("Usando análisis completo de cv_analyzer con IA")
            
            analysis_data = {
                "strengths": cv_analysis.get("strengths", []),
                "weaknesses": cv_analysis.get("weaknesses", []),
                "feedback": cv_analysis.get("feedback", ""),
                "structure": cv_analysis.get("structure", ""),
                "coherence": cv_analysis.get("coherence", ""),
                "experience": cv_analysis.get("experience", ""),
                "skills": cv_analysis.get("skills", []),
                "education": cv_analysis.get("education", []),
                "alerts": cv_analysis.get("alerts", [])
            }
        
        # Agregar información adicional del análisis completo
        if full_cv_data:
            # Agregar información de contacto si está disponible
            if full_cv_data.get("contacto"):
                contact_info = full_cv_data["contacto"]
                if contact_info.get("nombre"):
                    analysis_data["feedback"] += f" Nombre detectado: {contact_info['nombre']}."
                if contact_info.get("email"):
                    analysis_data["feedback"] += f" Email: {contact_info['email']}."
            
            # Agregar información de experiencia detallada
            if full_cv_data.get("experiencia_laboral"):
                exp_count = len(full_cv_data["experiencia_laboral"])
                analysis_data["feedback"] += f" Se detectaron {exp_count} experiencias laborales."
            
            # Agregar información de formación
            if full_cv_data.get("formacion_academica"):
                edu_count = len(full_cv_data["formacion_academica"])
                analysis_data["feedback"] += f" Se detectaron {edu_count} elementos de formación."
            
            # Agregar información de proyectos
            if full_cv_data.get("proyectos"):
                proj_count = len(full_cv_data["proyectos"])
                analysis_data["feedback"] += f" Se detectaron {proj_count} proyectos."
        
        logger.info(f"Análisis de CV completado para usuario {userId}")
        logger.info(f"Resultado final: {len(analysis_data.get('strengths', []))} fortalezas, {len(analysis_data.get('weaknesses', []))} debilidades")
        
        return CvAnalysis(**analysis_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en análisis de CV: {str(e)}")
        import traceback
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error procesando el CV: {str(e)}")

@app.post("/api/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """
    Sube un archivo CV y devuelve información básica del archivo.
    """
    try:
        # Verificar que sea un PDF
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            return JSONResponse(
                status_code=400, 
                content={"error": "Solo se permiten archivos PDF"}
            )
        
        # Leer el contenido del archivo
        contents = await file.read()
        
        # Verificar que sea un PDF válido
        try:
            pdf_reader = PdfReader(io.BytesIO(contents))
            num_pages = len(pdf_reader.pages)
        except Exception as e:
            return JSONResponse(
                status_code=400, 
                content={"error": f"Archivo PDF inválido: {str(e)}"}
            )
        
        # Devolver información del archivo
        return {
            "filename": file.filename,
            "size": len(contents),
            "pages": num_pages,
            "message": "CV subido correctamente"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"error": f"Error al procesar el archivo: {str(e)}"}
        )

@app.post("/api/pdf/generate-report")
async def generate_pdf_report(request: EmployabilityReportRequest):
    """
    Genera un PDF del informe de empleabilidad y lo devuelve para descarga.
    """
    logger.info(f"🔄 Iniciando generación de PDF para usuario: {request.fullName}")
    
    try:
        logger.info("📦 Importando servicio de PDF...")
        # Importar el servicio de PDF
        from pdf_service import create_employability_pdf
        logger.info("✅ Servicio de PDF importado correctamente")
        
        # Generar informe profesional de IA primero
        logger.info("🤖 Generando informe profesional de IA...")
        
        # Preparar el perfil completo para el análisis de IA
        perfil_completo = {
            "datos_personales": {
                "nombre": request.fullName,
                "user_id": request.userId
            },
            "habilidades_soft": [
                {
                    "habilidad": skill.skill,
                    "puntuacion": skill.score,
                    "nivel": skill.level,
                    "confianza": skill.confidence
                }
                for skill in request.softSkills
            ],
            "analisis_cv": request.cvAnalysis.dict() if request.cvAnalysis else {},
            "preferencias_laborales": request.jobPreferences.dict() if request.jobPreferences else {},
            "juegos_completados": request.completedGames,
            "logs_juegos": [log.dict() for log in request.logs] if request.logs else []
        }
        
        # Convertir a formato de texto para la IA
        perfil_texto = f"""
PERFIL COMPLETO DEL CANDIDATO:

DATOS PERSONALES:
- Nombre: {perfil_completo['datos_personales']['nombre']}
- ID: {perfil_completo['datos_personales']['user_id']}

HABILIDADES SOFT EVALUADAS:
{chr(10).join([f"- {h['habilidad']}: {h['puntuacion']}% (Nivel: {h['nivel']}, Confianza: {h['confianza']}%)" for h in perfil_completo['habilidades_soft']])}

ANÁLISIS DETALLADO DEL CV:
{format_cv_analysis(perfil_completo['analisis_cv']) if perfil_completo['analisis_cv'] else "No se proporcionó análisis de CV"}

PREFERENCIAS LABORALES:
{format_job_preferences(perfil_completo['preferencias_laborales']) if perfil_completo['preferencias_laborales'] else "No se especificaron preferencias laborales"}

JUEGOS COMPLETADOS:
{', '.join(perfil_completo['juegos_completados']) if perfil_completo['juegos_completados'] else "Ningún juego completado"}

LOGS DE JUEGOS:
{json.dumps(perfil_completo['logs_juegos'], indent=2, ensure_ascii=False) if perfil_completo['logs_juegos'] else "No hay logs de juegos disponibles"}
"""
        
        # Generar informe profesional usando IA
        informe_profesional = generar_informe(perfil_texto)
        logger.info("✅ Informe profesional de IA generado")
        
        # Preparar los datos para el PDF
        logger.info("📊 Preparando datos para el PDF...")
        # Convertir objetos Pydantic a diccionarios
        soft_skills_dict = [skill.dict() for skill in request.softSkills]
        cv_analysis_dict = request.cvAnalysis.dict() if request.cvAnalysis else {}
        job_preferences_dict = request.jobPreferences.dict() if request.jobPreferences else {}
        
        pdf_data = {
            "gameData": soft_skills_dict,
            "cvAnalysis": cv_analysis_dict,
            "jobPreferences": job_preferences_dict,
            "userInfo": {
                "fullName": request.fullName,
                "userId": request.userId
            },
            "informeProfesional": informe_profesional  # Incluir el informe profesional de IA
        }
        logger.info(f"📋 Datos preparados: {len(request.softSkills)} habilidades, CV: {bool(request.cvAnalysis)}, Preferencias: {bool(request.jobPreferences)}")
        
        # Generar el PDF
        logger.info("🖨️ Generando PDF...")
        start_time = datetime.now()
        pdf_buffer = create_employability_pdf(pdf_data)
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        logger.info(f"✅ PDF generado en {generation_time:.2f} segundos")
        
        # Crear un archivo temporal
        logger.info("📁 Creando archivo temporal...")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_buffer)
            tmp_file_path = tmp_file.name
        logger.info(f"📄 Archivo temporal creado: {tmp_file_path}")
        
        # Generar nombre de archivo
        filename = f"informe_empleabilidad_{request.fullName.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        logger.info(f"📝 Nombre de archivo: {filename}")
        
        # Devolver el archivo PDF
        logger.info("🚀 Enviando respuesta...")
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        
    except ImportError as e:
        logger.error(f"❌ Error importando servicio PDF: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Servicio de PDF no disponible"
        )
    except Exception as e:
        logger.error(f"❌ Error generando PDF: {str(e)}")
        logger.error(f"🔍 Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"📋 Traceback completo: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generando PDF: {str(e)}"
        )

@app.post("/api/pdf/test")
async def test_pdf_generation():
    """
    Endpoint de prueba para verificar la generación de PDF
    """
    logger.info("🧪 Iniciando prueba de generación de PDF...")
    
    try:
        logger.info("📊 Preparando datos de prueba...")
        # Datos de prueba simples
        test_data = {
            "gameData": [
                {"skill": "Comunicación", "score": 85, "level": "alto", "confidence": 90}
            ],
            "cvAnalysis": {"strengths": ["Test"], "weaknesses": []},
            "jobPreferences": {"areas": ["Test"], "needs": []},
            "userInfo": {"fullName": "Test User", "userId": "test123"}
        }
        logger.info("✅ Datos de prueba preparados")
        
        logger.info("📦 Importando servicio de PDF completo...")
        from pdf_service import create_employability_pdf
        logger.info("✅ Servicio importado")
        
        logger.info("🖨️ Generando PDF completo de prueba...")
        start_time = datetime.now()
        pdf_buffer = create_employability_pdf(test_data)
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        logger.info(f"✅ PDF de prueba generado en {generation_time:.2f} segundos")
        logger.info(f"📏 Tamaño del buffer: {len(pdf_buffer)} bytes")
        
        logger.info("📁 Creando archivo temporal...")
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_buffer)
            tmp_file_path = tmp_file.name
        logger.info(f"✅ Archivo temporal creado: {tmp_file_path}")
        
        logger.info("🚀 Preparando respuesta...")
        response = FileResponse(
            path=tmp_file_path,
            filename="test.pdf",
            media_type='application/pdf'
        )
        logger.info("✅ Respuesta preparada")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de PDF: {str(e)}")
        logger.error(f"🔍 Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))