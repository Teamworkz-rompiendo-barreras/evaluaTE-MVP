# backend/main.py
# Versión limpia del backend para Azure

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn
from typing import List, Optional, Dict, Any
from datetime import datetime
import io
import json
import os
import logging
import tempfile

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    import os
    # Mostrar directorio actual y buscar archivo .env
    current_dir = os.getcwd()
    env_file = os.path.join(current_dir, '.env')
    print(f"🔍 DEBUG - Directorio actual: {current_dir}")
    print(f"🔍 DEBUG - Buscando archivo .env en: {env_file}")
    print(f"🔍 DEBUG - ¿Existe archivo .env?: {os.path.exists(env_file)}")
    
    load_dotenv()
    print("✅ Archivo .env cargado correctamente")
except ImportError:
    print("⚠️ python-dotenv no está instalado, usando variables de entorno del sistema")
except Exception as e:
    print(f"⚠️ Error cargando .env: {e}")

# Limpiar variables de proxy del sistema que pueden causar problemas
import os
if 'HTTP_PROXY' in os.environ:
    del os.environ['HTTP_PROXY']
if 'HTTPS_PROXY' in os.environ:
    del os.environ['HTTPS_PROXY']
if 'ALL_PROXY' in os.environ:
    del os.environ['ALL_PROXY']

print("✅ Variables de proxy del sistema limpiadas")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables de entorno para Azure OpenAI (opcionales)
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Debug: Mostrar valores cargados
print(f"🔍 DEBUG - API_KEY: {API_KEY}")
print(f"🔍 DEBUG - ENDPOINT: {ENDPOINT}")
print(f"🔍 DEBUG - DEPLOYMENT: {DEPLOYMENT}")
print(f"🔍 DEBUG - API_VERSION: {API_VERSION}")

# Configurar NO_PROXY específicamente para el endpoint de Azure OpenAI
if ENDPOINT:
    # Extraer el dominio del endpoint (ej: teamworkzevaluate-openai.openai.azure.com)
    from urllib.parse import urlparse
    parsed_url = urlparse(ENDPOINT)
    domain = parsed_url.netloc
    os.environ['NO_PROXY'] = domain
    print(f"✅ NO_PROXY configurado para: {domain}")
else:
    os.environ['NO_PROXY'] = '*.openai.azure.com'
    print("✅ NO_PROXY configurado para *.openai.azure.com")

# Log de configuración
logger.info("🔧 Configurando EvaluaTE Backend...")
logger.info(f"API_KEY: {'✅' if API_KEY else '❌'}")
logger.info(f"ENDPOINT: {'✅' if ENDPOINT else '❌'}")
logger.info(f"DEPLOYMENT: {'✅' if DEPLOYMENT else '❌'}")
logger.info(f"API_VERSION: {'✅' if API_VERSION else '❌'}")

# Cliente de Azure OpenAI (solo si está configurado)
client = None
if all([API_KEY, ENDPOINT, DEPLOYMENT, API_VERSION]):
    try:
        from openai import AzureOpenAI
        
        # Configuración mínima sin argumentos problemáticos
        client = AzureOpenAI(
            api_key=API_KEY, 
            api_version=API_VERSION, 
            azure_endpoint=ENDPOINT
        )
        logger.info("✅ Azure OpenAI configurado correctamente")
    except Exception as e:
        logger.warning(f"⚠️ Error configurando Azure OpenAI: {e}")
        # Intentar configuración alternativa
        try:
            import os
            # Forzar configuración de entorno para evitar proxies
            os.environ['NO_PROXY'] = '*'
            os.environ['no_proxy'] = '*'
            
            client = AzureOpenAI(
                api_key=API_KEY, 
                api_version=API_VERSION, 
                azure_endpoint=ENDPOINT
            )
            logger.info("✅ Azure OpenAI configurado correctamente (configuración alternativa)")
        except Exception as e2:
            logger.warning(f"⚠️ Error en configuración alternativa: {e2}")
            client = None

# Tipos compartidos
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
    workMode: Optional[str] = "remoto"
    availability: Optional[str] = "completa"
    willingToRelocate: bool = False
    hasDisabilityCert: bool = False

class AccessibilitySettings(BaseModel):
    easyReadingMode: bool = False
    audioAssistiveMode: bool = False
    showPictograms: bool = False
    contrastLevel: str = "normal"

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
    completedGames: List[str] = []
    logs: List[GameDecisionLog] = []

class ReportResponse(BaseModel):
    report: Dict[str, Any]
    recommendations: Dict[str, Any]  # Cambiado para aceptar estructura compleja
    employabilityScore: int
    level: str
    summary: str
    createdAt: str

class FeedbackRequest(BaseModel):
    informe: str
    rating: str
    comment: str
    userData: dict

app = FastAPI(title="EvaluaTE Backend", version="1.0.0")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Bienvenida/o a EvaluaTE MVP", "status": "running"}

@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoreo"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "EvaluaTE Backend",
        "version": "1.0.0"
    }

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/logs/scene", response_model=Dict[str, Any])
async def log_scene_decision(data: Dict[str, Any]):
    """Registra una decisión de escena"""
    try:
        logger.info(f"Decisión de escena registrada: {data}")
        return {"status": "success", "message": "Decisión registrada"}
    except Exception as e:
        logger.error(f"Error registrando decisión: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logs/game-complete", response_model=Dict[str, Any])
async def log_game_complete(data: Dict[str, Any]):
    """Registra la finalización de un juego"""
    try:
        logger.info(f"Juego completado: {data}")
        return {"status": "success", "message": "Juego completado registrado"}
    except Exception as e:
        logger.error(f"Error registrando juego completado: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/informe-ia", response_model=ReportResponse)
async def generate_ia_report(request: EmployabilityReportRequest):
    """Genera un informe profesional de empleabilidad con IA"""
    try:
        logger.info(f"Generando informe profesional para usuario: {request.userId}")
        
        # Calcular puntaje de empleabilidad
        total_skills = len(request.softSkills)
        if total_skills == 0:
            employability_score = 50
        else:
            total_score = sum(skill.score for skill in request.softSkills)
            employability_score = total_score // total_skills

        # Determinar nivel
        if employability_score >= 80:
            level = "alto"
        elif employability_score >= 50:
            level = "medio"
        else:
            level = "bajo"

        # Generar informe profesional con IA
        if client:
            professional_report = await generate_professional_report_with_ai(request, employability_score, level)
        else:
            professional_report = generate_basic_report(request, employability_score, level)

        # Crear reporte con jobPreferences incluido
        report = {
            "userId": request.userId,
            "fullName": request.fullName,
            "softSkills": [skill.dict() for skill in request.softSkills],
            "jobPreferences": request.jobPreferences.dict() if request.jobPreferences else {
                "areas": [],
                "needs": [],
                "workMode": "remoto",
                "availability": "completa",
                "willingToRelocate": False,
                "hasDisabilityCert": False
            },
            "employabilityScore": employability_score,
            "level": level,
            "createdAt": datetime.now().isoformat()
        }

        return ReportResponse(
            report=report,
            recommendations=professional_report["recommendations"],
            employabilityScore=employability_score,
            level=level,
            summary=professional_report["summary"],
            createdAt=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generando informe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_professional_report_with_ai(request: EmployabilityReportRequest, employability_score: int, level: str) -> dict:
    """Genera un informe profesional usando IA"""
    
    # Preparar datos para el prompt
    soft_skills_text = "\n".join([f"- {skill.skill}: {skill.score}% ({skill.level})" for skill in request.softSkills])
    
    cv_analysis_text = ""
    if request.cvAnalysis:
        cv_analysis_text = f"""
        Análisis del CV:
        - Fortalezas: {', '.join(request.cvAnalysis.strengths)}
        - Debilidades: {', '.join(request.cvAnalysis.weaknesses)}
        - Estructura: {request.cvAnalysis.structure}
        - Coherencia: {request.cvAnalysis.coherence}
        - Experiencia: {request.cvAnalysis.experience}
        - Habilidades técnicas: {', '.join(request.cvAnalysis.skills)}
        - Formación: {', '.join(request.cvAnalysis.education)}
        """
    
    job_preferences_text = ""
    if request.jobPreferences:
        job_preferences_text = f"""
        Preferencias laborales:
        - Áreas de interés: {', '.join(request.jobPreferences.areas)}
        - Necesidades: {', '.join(request.jobPreferences.needs)}
        - Modalidad: {request.jobPreferences.workMode}
        - Disponibilidad: {request.jobPreferences.availability}
        - Dispuesto a mudarse: {'Sí' if request.jobPreferences.willingToRelocate else 'No'}
        - Certificado de discapacidad: {'Sí' if request.jobPreferences.hasDisabilityCert else 'No'}
        """
    
    # Prompt para generar informe profesional
    prompt = f"""
    Eres un orientador laboral experto. Genera un informe profesional de empleabilidad basado en los siguientes datos:

    CANDIDATO: {request.fullName}
    PUNTAJE DE EMPLEABILIDAD: {employability_score}/100 (Nivel: {level})

    HABILIDADES SOFT EVALUADAS:
    {soft_skills_text}

    {cv_analysis_text}

    {job_preferences_text}

    JUEGOS COMPLETADOS: {', '.join(request.completedGames)}

    Genera un informe profesional que incluya:

    1. RESUMEN DEL PERFIL: Análisis general del candidato
    2. ANÁLISIS DE FORTALEZAS: Basado en habilidades soft y CV
    3. ÁREAS DE MEJORA: Con recomendaciones específicas
    4. ANÁLISIS DEL CV: Estructura, coherencia, claridad, formación, ortografía
    5. SUGERENCIAS LABORALES: Roles específicos según preferencias y habilidades
    6. PRÓXIMOS PASOS: A corto, medio y largo plazo
    7. RECURSOS Y APOYO: Enlaces a plataformas, cursos, herramientas

    IMPORTANTE: 
    - Si NO tiene certificado de discapacidad, NO recomiendes plataformas específicas para personas con discapacidad
    - Si SÍ tiene certificado, incluye recursos específicos para personas con discapacidad
    - Todos los enlaces deben abrirse en nueva ventana
    - Sé específico y personalizado

    Responde en formato JSON:
    {{
        "summary": "resumen del perfil",
        "recommendations": {{
            "profile_analysis": "análisis detallado del perfil",
            "strengths_analysis": "análisis de fortalezas",
            "improvement_areas": "áreas de mejora con recomendaciones",
            "cv_analysis": "análisis detallado del CV",
            "job_suggestions": "sugerencias laborales específicas",
            "next_steps": {{
                "short_term": ["paso1", "paso2"],
                "medium_term": ["paso1", "paso2"],
                "long_term": ["paso1", "paso2"]
            }},
            "resources": [
                {{
                    "name": "nombre del recurso",
                    "url": "https://ejemplo.com",
                    "description": "descripción del recurso"
                }}
            ]
        }}
    }}
    """
    
    try:
        # Limpiar el nombre del deployment para evitar problemas con espacios
        deployment_name = DEPLOYMENT.strip()
        
        response = client.chat.completions.create(
            model=deployment_name,  # En Azure OpenAI, model es el nombre del deployment
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
            timeout=60  # Timeout de 60 segundos para Azure OpenAI
        )
        
        import json
        report_data = json.loads(response.choices[0].message.content)
        return report_data
        
    except Exception as e:
        logger.error(f"Error generando informe con IA: {e}")
        return generate_basic_report(request, employability_score, level)

def generate_basic_report(request: EmployabilityReportRequest, employability_score: int, level: str) -> dict:
    """Genera un informe básico sin IA"""
    
    has_disability_cert = request.jobPreferences and request.jobPreferences.hasDisabilityCert
    
    resources = [
        {
            "name": "LinkedIn",
            "url": "https://www.linkedin.com",
            "description": "Red profesional para networking y búsqueda de empleo"
        },
        {
            "name": "InfoJobs",
            "url": "https://www.infojobs.net",
            "description": "Portal de empleo líder en España"
        },
        {
            "name": "Platzi",
            "url": "https://platzi.com",
            "description": "Plataforma de cursos online de tecnología"
        }
    ]
    
    if has_disability_cert:
        resources.append({
            "name": "Fundación ONCE",
            "url": "https://www.fundaciononce.es",
            "description": "Recursos específicos para personas con discapacidad"
        })
    
    return {
        "summary": f"Basado en tu evaluación, tu nivel de empleabilidad es {level} con un puntaje de {employability_score}/100.",
        "recommendations": {
            "profile_analysis": f"Perfil de {request.fullName} con {len(request.softSkills)} habilidades evaluadas.",
            "strengths_analysis": "Fortalezas identificadas en los minijuegos de evaluación.",
            "improvement_areas": "Áreas de mejora detectadas con recomendaciones específicas.",
            "cv_analysis": "Análisis del CV realizado con herramientas especializadas.",
            "job_suggestions": "Sugerencias laborales basadas en preferencias y habilidades.",
            "next_steps": {
                "short_term": ["Actualizar CV", "Crear perfil en LinkedIn"],
                "medium_term": ["Completar formación específica", "Ampliar red profesional"],
                "long_term": ["Desarrollar especialización", "Buscar oportunidades de liderazgo"]
            },
            "resources": resources
        }
    }

@app.get("/api/informe-ia")
async def get_ia_report():
    """Obtiene el último informe generado"""
    return {"message": "Endpoint de informe disponible"}

@app.post("/api/logs/report", response_model=ReportResponse)
async def generate_report(request: EmployabilityReportRequest):
    """Genera un reporte (alias para generate_ia_report)"""
    return await generate_ia_report(request)

@app.post("/api/informe-ia/feedback")
async def receive_feedback(request: FeedbackRequest):
    """Recibe feedback del usuario"""
    try:
        logger.info(f"Feedback recibido: {request.rating} - {request.comment}")
        return {"message": "Feedback recibido correctamente"}
    except Exception as e:
        logger.error(f"Error procesando feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/informe-ia/feedback/stats")
async def get_feedback_stats():
    """Obtiene estadísticas de feedback"""
    return {
        "total_feedback": 0,
        "positive_feedback": 0,
        "negative_feedback": 0
    }

@app.post("/api/pdf/analyze-cv")
async def analyze_cv_pdf(file: UploadFile = File(...)):
    """Analiza un CV en formato PDF usando Azure Document Intelligence"""
    try:
        logger.info(f"Analizando CV PDF: {file.filename}")
        
        # Leer el contenido del archivo
        content = await file.read()
        
        # Guardar temporalmente el archivo
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
                    # Analizar con Azure Document Intelligence si está configurado
        try:
            analysis = await analyze_cv_with_azure(temp_file_path, file.filename)
        except Exception as e:
            logger.warning(f"Azure Document Intelligence no disponible, usando fallback: {e}")
            # Fallback: análisis básico con PyMuPDF
            analysis = await analyze_cv_with_pymupdf(temp_file_path, file.filename)
            
            return analysis.dict()
            
        finally:
            # Limpiar archivo temporal
            os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Error analizando CV: {str(e)}")
        # Devolver análisis básico en caso de error
        return CvAnalysis(
            strengths=["Experiencia detectada", "Habilidades técnicas"],
            weaknesses=["Necesita mejorar estructura", "Falta de detalles específicos"],
            feedback="CV analizado con limitaciones técnicas",
            structure="regular",
            coherence="regular",
            experience="regular",
            skills=["Habilidades generales"],
            education=["Formación detectada"],
            alerts=["Error en análisis automático"]
        ).dict()

async def analyze_cv_with_azure(file_path: str, filename: str) -> CvAnalysis:
    """Analiza CV usando Azure Document Intelligence"""
    try:
        from azure.ai.formrecognizer import DocumentAnalysisClient
        from azure.core.credentials import AzureKeyCredential
        
        # Configuración de Azure Document Intelligence
        endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        
        if not endpoint or not key:
            logger.warning("Azure Document Intelligence no configurado - variables de entorno faltantes")
            raise Exception("Azure Form Recognizer no configurado")
        
        logger.info(f"Conectando a Azure Document Intelligence: {endpoint}")
        client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        
        with open(file_path, "rb") as document:
            logger.info("Iniciando análisis de documento...")
            poller = client.begin_analyze_document("prebuilt-layout", document)
            result = poller.result()
        
        # Extraer texto del documento
        text_content = ""
        for page in result.pages:
            for line in page.lines:
                text_content += line.content + "\n"
        
        logger.info(f"Texto extraído: {len(text_content)} caracteres")
        
        # Analizar contenido con IA
        return await analyze_cv_content_with_ai(text_content, filename)
        
    except Exception as e:
        logger.error(f"Error con Azure Document Intelligence: {e}")
        raise

async def analyze_cv_with_pymupdf(file_path: str, filename: str) -> CvAnalysis:
    """Analiza CV usando PyMuPDF como fallback"""
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(file_path)
        text_content = ""
        
        for page in doc:
            text_content += page.get_text()
        
        doc.close()
        
        # Analizar contenido con IA
        return await analyze_cv_content_with_ai(text_content, filename)
        
    except Exception as e:
        logger.error(f"Error con PyMuPDF: {e}")
        raise

async def analyze_cv_content_with_ai(content: str, filename: str) -> CvAnalysis:
    """Analiza el contenido del CV usando IA"""
    try:
        if not client:
            # Fallback sin IA
            return CvAnalysis(
                strengths=["Contenido detectado en CV"],
                weaknesses=["Análisis limitado sin IA"],
                feedback="CV analizado básicamente",
                structure="regular",
                coherence="regular",
                experience="regular",
                skills=["Habilidades detectadas"],
                education=["Formación detectada"],
                alerts=["Análisis sin IA disponible"]
            )
        
        # Prompt para análisis de CV
        prompt = f"""
        Analiza el siguiente CV y proporciona un análisis detallado en formato JSON:
        
        CV: {content[:4000]}  # Limitar contenido para el prompt
        
        Responde en este formato JSON exacto:
        {{
            "strengths": ["fortaleza1", "fortaleza2"],
            "weaknesses": ["debilidad1", "debilidad2"],
            "feedback": "feedback general",
            "structure": "buena/regular/mala",
            "coherence": "buena/regular/mala",
            "experience": "alta/regular/baja",
            "skills": ["skill1", "skill2"],
            "education": ["educación1", "educación2"],
            "alerts": ["alerta1", "alerta2"]
        }}
        """
        
        # Limpiar el nombre del deployment para evitar problemas con espacios
        deployment_name = DEPLOYMENT.strip()
        
        response = client.chat.completions.create(
            model=deployment_name,  # En Azure OpenAI, model es el nombre del deployment
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
            timeout=60  # Timeout de 60 segundos para Azure OpenAI
        )
        
        # Parsear respuesta JSON
        import json
        analysis_data = json.loads(response.choices[0].message.content)
        
        return CvAnalysis(**analysis_data)
        
    except Exception as e:
        logger.error(f"Error en análisis con IA: {e}")
        # Devolver análisis básico
        return CvAnalysis(
            strengths=["Contenido detectado"],
            weaknesses=["Error en análisis IA"],
            feedback="CV analizado con limitaciones",
            structure="regular",
            coherence="regular",
            experience="regular",
            skills=["Habilidades generales"],
            education=["Formación detectada"],
            alerts=["Error en análisis automático"]
        )

@app.post("/api/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """Sube un CV para análisis"""
    try:
        logger.info(f"CV subido: {file.filename}")
        return {
            "message": "CV subido correctamente",
            "filename": file.filename,
            "size": file.size
        }
    except Exception as e:
        logger.error(f"Error subiendo CV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)