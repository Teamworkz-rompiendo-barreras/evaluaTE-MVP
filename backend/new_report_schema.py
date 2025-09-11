# backend/new_report_schema.py
# Nuevo esquema de informe estructurado para el backend

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class PersonalData(BaseModel):
    name: str
    location: str
    email: str
    phone: str
    disability_certificate: str


class ImprovementArea(BaseModel):
    area: str
    reason: str
    suggested_action: str


class CvEvidence(BaseModel):
    structure: str
    coherence: str
    key_info: str
    clarity: str
    style: str


class CvAnalysis(BaseModel):
    structure_score: int = Field(ge=1, le=5)
    coherence_score: int = Field(ge=1, le=5)
    key_info_score: int = Field(ge=1, le=5)
    clarity_score: int = Field(ge=1, le=5)
    style_score: int = Field(ge=1, le=5)
    evidence: CvEvidence
    corrections: List[str] = Field(default_factory=list)
    reordering_suggestions: List[str] = Field(default_factory=list)


class SuggestedRole(BaseModel):
    role: str
    reason: str
    seniority: str
    remote_viable: bool


class ActionPlan(BaseModel):
    short_term: List[str]
    medium_term: List[str]
    long_term: List[str]


class JobSearchAdvice(BaseModel):
    cv_optimization: List[str]
    letters_portfolio: str
    recommended_platforms: List[str]
    networking: str
    interview_tips: str


class UsefulTools(BaseModel):
    productivity: List[str]
    job_search: List[str]
    learning: List[str]
    accessibility: List[str]


class NewReportSchema(BaseModel):
    summary: str
    personal_data: PersonalData
    profile_summary: str
    cv_summary: str
    strengths: List[str]
    improvement_areas: List[ImprovementArea]
    cv_analysis: CvAnalysis
    ideal_work_environment: str
    suggested_roles: List[SuggestedRole]
    action_plan: ActionPlan
    job_search_advice: JobSearchAdvice
    useful_tools: UsefulTools
    completed_games: List[str]
    final_message: str


def create_default_report(full_name: str, soft_skills: List[Dict[str, Any]], cv_analysis: Dict[str, Any], job_preferences: Dict[str, Any]) -> NewReportSchema:
    """
    Crea un reporte por defecto con el nuevo esquema estructurado
    """
    # Extraer fortalezas de soft skills y crear formato compatible con frontend
    strengths = []
    if soft_skills:
        for skill in soft_skills:
            if isinstance(skill, dict) and skill.get('name'):
                strengths.append(skill['name'])
            elif isinstance(skill, str):
                strengths.append(skill)
    
    # Si no hay fortalezas, crear algunas por defecto
    if not strengths:
        strengths = [
            "Capacidad de aprendizaje",
            "Adaptabilidad al cambio",
            "Trabajo en equipo"
        ]
    
    # Crear datos personales básicos
    personal_data = PersonalData(
        name=full_name or "Usuario",
        location=getattr(job_preferences, 'location', 'No especificado') if job_preferences else 'No especificado',
        email="No proporcionado",
        phone="No proporcionado",
        disability_certificate="No" if not job_preferences or not getattr(job_preferences, 'hasDisabilityCert', False) else "Sí"
    )
    
    # Crear análisis del CV por defecto
    cv_evidence = CvEvidence(
        structure="CV analizado con información limitada",
        coherence="Se requiere más información para evaluar la coherencia",
        key_info="Información básica disponible",
        clarity="Formato estándar",
        style="Presentación profesional"
    )
    
    cv_analysis_data = CvAnalysis(
        structure_score=3,
        coherence_score=3,
        key_info_score=3,
        clarity_score=3,
        style_score=3,
        evidence=cv_evidence,
        corrections=[
            "Incluir más detalles sobre logros específicos",
            "Añadir métricas cuantificables",
            "Especificar tecnologías y herramientas utilizadas"
        ],
        reordering_suggestions=[
            "Priorizar experiencia laboral más reciente",
            "Destacar habilidades técnicas relevantes"
        ]
    )
    
    # Crear plan de acción por defecto
    action_plan = ActionPlan(
        short_term=[
            "Actualizar CV con información más detallada",
            "Crear perfil en LinkedIn",
            "Identificar 3-5 empresas objetivo"
        ],
        medium_term=[
            "Completar formación en habilidades técnicas",
            "Ampliar red profesional",
            "Preparar portfolio de proyectos"
        ],
        long_term=[
            "Desarrollar especialización técnica",
            "Buscar oportunidades de liderazgo",
            "Considerar certificaciones profesionales"
        ]
    )
    
    # Crear consejos de búsqueda por defecto
    job_search_advice = JobSearchAdvice(
        cv_optimization=[
            "Usar palabras clave específicas del sector",
            "Incluir logros cuantificables",
            "Destacar proyectos relevantes"
        ],
        letters_portfolio="Preparar carta de presentación personalizada para cada empresa",
        recommended_platforms=["LinkedIn", "InfoJobs", "Indeed", "Stack Overflow Jobs"],
        networking="Participar en meetups y grupos profesionales online",
        interview_tips="Preparar respuestas STAR y practicar presentación de proyectos"
    )
    
    # Crear herramientas útiles por defecto
    useful_tools = UsefulTools(
        productivity=["Trello", "Notion", "Google Calendar"],
        job_search=["LinkedIn", "Glassdoor", "Resume.io"],
        learning=["Coursera", "edX", "Platzi", "Udemy"],
        accessibility=["Microsoft Immersive Reader", "Grammarly", "ColorZilla"]
    )
    
    # Crear roles sugeridos por defecto
    suggested_roles = [
        SuggestedRole(
            role="Desarrollador Junior",
            reason="Perfil adecuado para roles de entrada con potencial de crecimiento",
            seniority="Junior",
            remote_viable=True
        )
    ]
    
    return NewReportSchema(
        summary=f"Informe de empleabilidad para {full_name}",
        personal_data=personal_data,
        profile_summary="Perfil profesional con potencial de desarrollo. Se recomienda fortalecer habilidades técnicas específicas y experiencia práctica.",
        cv_summary="CV con información básica disponible. Se sugiere enriquecer con más detalles sobre proyectos y logros específicos.",
        strengths=strengths,
        improvement_areas=[
            ImprovementArea(
                area="Experiencia técnica",
                reason="Necesita más práctica en tecnologías específicas",
                suggested_action="Completar proyectos prácticos y cursos online"
            ),
            ImprovementArea(
                area="Métricas de logros",
                reason="Faltan resultados cuantificables",
                suggested_action="Incluir números y porcentajes en el CV"
            )
        ],
        cv_analysis=cv_analysis_data,
        ideal_work_environment="Entorno inclusivo con oportunidades de aprendizaje y crecimiento profesional. Preferencia por empresas que valoren el desarrollo continuo.",
        suggested_roles=suggested_roles,
        action_plan=action_plan,
        job_search_advice=job_search_advice,
        useful_tools=useful_tools,
        completed_games=["Evaluación de habilidades básicas completada"],
        final_message=f"{full_name}, tu perfil muestra un excelente potencial para el desarrollo profesional. Enfócate en construir experiencia práctica y desarrollar habilidades técnicas específicas. La constancia y el aprendizaje continuo serán tus mejores aliados en la búsqueda de empleo."
    )


def convert_old_format_to_new(old_data: Dict[str, Any]) -> NewReportSchema:
    """
    Convierte datos del formato antiguo al nuevo esquema estructurado
    """
    # Extraer información del formato antiguo
    report = old_data.get('report', {})
    recommendations = old_data.get('recommendations', [])
    
    full_name = report.get('fullName', 'Usuario')
    resumen = report.get('resumen_ejecutivo', 'Resumen no disponible')
    
    # Crear reporte por defecto
    default_report = create_default_report(full_name, [], {}, {})
    
    # Sobrescribir con datos disponibles del formato antiguo
    if resumen and resumen != 'Resumen no disponible':
        default_report.profile_summary = resumen
        default_report.cv_summary = resumen
    
    # Manejar recommendations de forma segura
    if recommendations:
        if isinstance(recommendations, list) and len(recommendations) > 0:
            # Tomar las primeras 5 recomendaciones como fortalezas
            default_report.strengths = recommendations[:5] if len(recommendations) >= 5 else recommendations
        elif isinstance(recommendations, dict) and len(recommendations) > 0:
            # Si recommendations es un dict, extraer las claves relevantes
            keys = list(recommendations.keys())
            default_report.strengths = keys[:5] if len(keys) >= 5 else keys
        else:
            # Si no hay recommendations válidas, usar fortalezas por defecto
            default_report.strengths = ["Liderazgo", "Comunicación", "Trabajo en equipo", "Resolución de problemas", "Creatividad"]
    else:
        # Si no hay recommendations, usar fortalezas por defecto
        default_report.strengths = ["Liderazgo", "Comunicación", "Trabajo en equipo", "Resolución de problemas", "Creatividad"]
    
    # Ajustar puntuación si está disponible
    score = old_data.get('employabilityScore')
    if score is not None:
        # Ajustar análisis del CV basado en la puntuación
        if score >= 80:
            default_report.cv_analysis.structure_score = 5
            default_report.cv_analysis.coherence_score = 5
        elif score >= 60:
            default_report.cv_analysis.structure_score = 4
            default_report.cv_analysis.coherence_score = 4
        elif score >= 40:
            default_report.cv_analysis.structure_score = 3
            default_report.cv_analysis.coherence_score = 3
        else:
            default_report.cv_analysis.structure_score = 2
            default_report.cv_analysis.coherence_score = 2
    
    return default_report


def create_frontend_compatible_data(full_name: str, soft_skills: List[Dict[str, Any]], cv_analysis: Dict[str, Any], job_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea datos en el formato que espera el frontend actual
    """
    # Crear soft skills con formato que espera el frontend
    formatted_soft_skills = []
    if soft_skills:
        for skill in soft_skills:
            if isinstance(skill, dict):
                if skill.get('name') and skill.get('score'):
                    formatted_soft_skills.append({
                        'skill': skill['name'],
                        'score': skill['score']
                    })
                elif skill.get('skill') and skill.get('score'):
                    formatted_soft_skills.append({
                        'skill': skill['skill'],
                        'score': skill['score']
                    })
            elif isinstance(skill, str):
                formatted_soft_skills.append({
                    'skill': skill,
                    'score': 70  # Score por defecto
                })
    
    # Si no hay soft skills, crear algunas por defecto
    if not formatted_soft_skills:
        formatted_soft_skills = [
            {'skill': 'Liderazgo', 'score': 90},
            {'skill': 'Comunicación', 'score': 85},
            {'skill': 'Trabajo en equipo', 'score': 80},
            {'skill': 'Resolución de problemas', 'score': 75},
            {'skill': 'Creatividad', 'score': 70}
        ]
    
    # Crear áreas de mejora
    improvement_areas = [
        {
            'area': 'Experiencia técnica',
            'reason': 'Necesita más práctica en tecnologías específicas'
        },
        {
            'area': 'Métricas de logros',
            'reason': 'Faltan resultados cuantificables'
        }
    ]
    
    # Crear plan de acción
    action_plan = {
        'short_term': [
            'Actualizar CV con información más detallada',
            'Crear perfil en LinkedIn',
            'Identificar 3-5 empresas objetivo'
        ],
        'medium_term': [
            'Completar formación en habilidades técnicas',
            'Ampliar red profesional',
            'Preparar portfolio de proyectos'
        ],
        'long_term': [
            'Desarrollar especialización técnica',
            'Buscar oportunidades de liderazgo',
            'Considerar certificaciones profesionales'
        ]
    }
    
    # Crear análisis del CV
    cv_analysis_data = {
        'structure': getattr(cv_analysis, 'structure', 'regular') if cv_analysis else 'regular',
        'coherence': getattr(cv_analysis, 'coherence', 'regular') if cv_analysis else 'regular',
        'feedback': getattr(cv_analysis, 'feedback', 'CV analizado con limitaciones') if cv_analysis else 'CV analizado con limitaciones',
        'summary': 'gestión y coordinación de proyectos',
        'experience': [
            {'title': 'Gestión de proyectos y coordinación'}
        ],
        'education': [
            {'degree': 'Formación en gestión y administración'}
        ],
        'software': ['Microsoft Office', 'herramientas de gestión']
    }
    
    # Crear consejos de búsqueda
    job_search_advice = {
        'cv_optimization': ['gestión', 'coordinación', 'liderazgo']
    }
    
    # Crear herramientas útiles
    useful_tools = {
        'productivity': ['Excel', 'Google Sheets'],
        'job_search': ['LinkedIn', 'Indeed'],
        'learning': ['Coursera', 'Udemy']
    }
    
    # Crear roles sugeridos
    suggested_roles = [
        {
            'role': 'Coordinador de Proyectos',
            'reason': 'Perfil adecuado para roles de coordinación',
            'seniority': 'Junior-Mid',
            'remote_viable': True
        }
    ]
    
    # Crear juegos completados
    completed_games = ['Evaluación de habilidades básicas completada']
    
    return {
        'softSkills': formatted_soft_skills,
        'improvement_areas': improvement_areas,
        'action_plan': action_plan,
        'cv_analysis': cv_analysis_data,
        'job_search_advice': job_search_advice,
        'useful_tools': useful_tools,
        'suggested_roles': suggested_roles,
        'completed_games': completed_games,
        'employabilityScore': 76,  # Score por defecto
        'level': 'Intermedio'
    }
