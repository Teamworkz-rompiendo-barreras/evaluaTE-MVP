# backend/new_report_schema.py
# Nuevo esquema de informe estructurado para el backend

from typing import List, Dict, Any, Iterable
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


class CvDetails(BaseModel):
    experience: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)


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


class JobPreferences(BaseModel):
    location: str = ""
    work_mode: str = ""
    areas: List[str] = Field(default_factory=list)
    preferred_platforms: List[str] = Field(default_factory=list)
    seniority: str = ""
    has_disability_cert: bool = False


class NewReportSchema(BaseModel):
    summary: str
    personal_data: PersonalData
    profile_summary: str
    cv_summary: str
    cv_details: CvDetails = Field(default_factory=CvDetails)
    strengths: List[str]
    soft_skills: List[Dict[str, Any]]
    improvement_areas: List[ImprovementArea]
    cv_analysis: CvAnalysis
    ideal_work_environment: str
    suggested_roles: List[SuggestedRole]
    action_plan: ActionPlan
    job_search_advice: JobSearchAdvice
    job_preferences: JobPreferences = Field(default_factory=JobPreferences)
    useful_tools: UsefulTools
    employability_score: int
    completed_games: List[str]
    final_message: str


def _iter_items(source: Any) -> Iterable[Any]:
    if source is None:
        return []
    if isinstance(source, (list, tuple, set)):
        return list(source)
    return [source]


def _stringify_entries(entries: Any, priority_keys: Iterable[str] = ()) -> List[str]:
    normalized: List[str] = []
    keys = list(priority_keys or [])
    for item in _iter_items(entries):
        text = ""
        if isinstance(item, str):
            text = item.strip()
        elif isinstance(item, dict):
            parts: List[str] = []
            used_keys = set()
            for key in keys:
                if key in item:
                    value = item.get(key)
                    if isinstance(value, (list, dict)) or value is None:
                        continue
                    value_str = str(value).strip()
                    if value_str:
                        parts.append(value_str)
                        used_keys.add(key)
            if not parts:
                for key, value in item.items():
                    if key in used_keys or isinstance(value, (list, dict)) or value is None:
                        continue
                    value_str = str(value).strip()
                    if value_str:
                        parts.append(value_str)
            text = " — ".join(parts)
        elif item is not None:
            text = str(item).strip()
        if text:
            normalized.append(text)

    unique: List[str] = []
    seen = set()
    for entry in normalized:
        key = entry.lower()
        if key not in seen:
            seen.add(key)
            unique.append(entry)
    return unique


def _normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes", "si", "sí"}:
            return True
        if text in {"false", "0", "no"}:
            return False
    return False


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def create_default_report(full_name: str, soft_skills: List[Dict[str, Any]], cv_analysis: Dict[str, Any], job_preferences: Dict[str, Any]) -> NewReportSchema:
    """
    Crea un reporte por defecto con el nuevo esquema estructurado
    """
    # Formatear soft skills y derivar fortalezas
    formatted_soft_skills: List[Dict[str, Any]] = []
    if soft_skills:
        for skill in soft_skills:
            if isinstance(skill, dict):
                name = skill.get('name') or skill.get('skill')
                if name:
                    formatted_soft_skills.append({
                        'skill': name,
                        'score': skill.get('score', 70)
                    })
            elif isinstance(skill, str):
                formatted_soft_skills.append({'skill': skill, 'score': 70})

    # Si no hay soft skills, crear algunas por defecto
    if not formatted_soft_skills:
        formatted_soft_skills = [
            {'skill': 'Capacidad de aprendizaje', 'score': 85},
            {'skill': 'Adaptabilidad al cambio', 'score': 80},
            {'skill': 'Trabajo en equipo', 'score': 75}
        ]

    strengths = [s['skill'] for s in formatted_soft_skills if s.get('skill')]

    # Calcular puntaje global de empleabilidad como promedio de soft skills
    employability_score = int(
        sum(s.get('score', 0) for s in formatted_soft_skills) / len(formatted_soft_skills)
    ) if formatted_soft_skills else 0
    
    job_pref_input = job_preferences.copy() if isinstance(job_preferences, dict) else {}

    # Crear datos personales básicos
    personal_location = _safe_str(job_pref_input.get("location")) or "No especificado"
    personal_data = PersonalData(
        name=full_name or "Usuario",
        location=personal_location,
        email="No proporcionado",
        phone="No proporcionado",
        disability_certificate="Sí" if _normalize_bool(job_pref_input.get("hasDisabilityCert")) else "No",
    )
    
    # Crear análisis del CV tomando datos de entrada cuando existan
    cv_evidence_input = (cv_analysis or {}).get('evidence', {})
    cv_evidence = CvEvidence(
        structure=cv_evidence_input.get('structure', 'CV analizado con información limitada'),
        coherence=cv_evidence_input.get('coherence', 'Se requiere más información para evaluar la coherencia'),
        key_info=cv_evidence_input.get('key_info', 'Información básica disponible'),
        clarity=cv_evidence_input.get('clarity', 'Formato estándar'),
        style=cv_evidence_input.get('style', 'Presentación profesional'),
    )

    cv_analysis_data = CvAnalysis(
        structure_score=(cv_analysis or {}).get('structure_score', 3),
        coherence_score=(cv_analysis or {}).get('coherence_score', 3),
        key_info_score=(cv_analysis or {}).get('key_info_score', 3),
        clarity_score=(cv_analysis or {}).get('clarity_score', 3),
        style_score=(cv_analysis or {}).get('style_score', 3),
        evidence=cv_evidence,
        corrections=(cv_analysis or {}).get('corrections', [
            'Incluir más detalles sobre logros específicos',
            'Añadir métricas cuantificables',
            'Especificar tecnologías y herramientas utilizadas',
        ]),
        reordering_suggestions=(cv_analysis or {}).get('reordering_suggestions', [
            'Priorizar experiencia laboral más reciente',
            'Destacar habilidades técnicas relevantes',
        ]),
    )

    cv_details_input = (cv_analysis or {}).get('cv_details') if isinstance((cv_analysis or {}).get('cv_details'), dict) else {}
    experience_input = (
        cv_details_input.get('experience')
        or (cv_analysis or {}).get('experience')
        or (cv_analysis or {}).get('experience_detailed')
        or []
    )
    education_input = (
        cv_details_input.get('education')
        or (cv_analysis or {}).get('education')
        or (cv_analysis or {}).get('education_detailed')
        or []
    )
    languages_input = (
        cv_details_input.get('languages')
        or (cv_analysis or {}).get('languages')
        or (cv_analysis or {}).get('idiomas')
        or []
    )
    software_input = (
        cv_details_input.get('tools')
        or (cv_analysis or {}).get('software')
        or (cv_analysis or {}).get('tools')
        or (cv_analysis or {}).get('skills')
        or []
    )

    experience_details = _stringify_entries(
        experience_input,
        (
            'title',
            'role',
            'position',
            'company',
            'organization',
            'employer',
            'location',
            'start_date',
            'end_date',
            'duration',
            'description',
        ),
    )
    education_details = _stringify_entries(
        education_input,
        (
            'degree',
            'title',
            'program',
            'area',
            'institution',
            'school',
            'location',
            'start_date',
            'end_date',
            'graduation_year',
            'description',
        ),
    )
    language_details = _stringify_entries(
        languages_input,
        (
            'name',
            'language',
            'level',
            'certification',
        ),
    )
    software_details = _stringify_entries(
        software_input,
        (
            'name',
            'tool',
            'technology',
            'software',
            'level',
            'category',
        ),
    )

    cv_details = CvDetails(
        experience=experience_details,
        education=education_details,
        languages=language_details,
        tools=software_details,
    )

    feedback_text = (cv_analysis or {}).get(
        'feedback',
        'CV con información básica disponible. Se sugiere enriquecer con más detalles sobre proyectos y logros específicos.',
    )
    if not feedback_text:
        feedback_text = 'CV con información básica disponible. Se sugiere enriquecer con más detalles sobre proyectos y logros específicos.'

    cv_summary_lines: List[str] = []
    feedback_line = str(feedback_text).strip()
    if feedback_line:
        cv_summary_lines.append(feedback_line)

    def _append_section(title: str, items: List[str]) -> None:
        markdown_items = [f"- {entry}" for entry in items if entry]
        if not markdown_items:
            return
        cv_summary_lines.append("")
        cv_summary_lines.append(f"### {title}")
        cv_summary_lines.extend(markdown_items)

    _append_section('Experiencia destacada', experience_details)
    _append_section('Formación', education_details)
    _append_section('Idiomas', language_details)
    _append_section('Herramientas y tecnología', software_details)

    cv_summary_markdown = "\n".join(line for line in cv_summary_lines if line is not None).strip()
    # Determinar áreas de mejora usando datos del CV cuando existan
    improvement_areas: List[ImprovementArea] = []
    if cv_analysis and (cv_analysis.get('corrections') or cv_analysis.get('reordering_suggestions')):
        for c in cv_analysis.get('corrections', []):
            improvement_areas.append(ImprovementArea(area=c, reason='Corrección sugerida', suggested_action=c))
        for s in cv_analysis.get('reordering_suggestions', []):
            improvement_areas.append(ImprovementArea(area=s, reason='Sugerencia de reordenamiento', suggested_action=s))
    else:
        improvement_areas = [
            ImprovementArea(
                area='Experiencia técnica',
                reason='Necesita más práctica en tecnologías específicas',
                suggested_action='Completar proyectos prácticos y cursos online',
            ),
            ImprovementArea(
                area='Métricas de logros',
                reason='Faltan resultados cuantificables',
                suggested_action='Incluir números y porcentajes en el CV',
            ),
        ]

    work_mode_pref = _safe_str(job_pref_input.get('workMode') or job_pref_input.get('work_mode'))
    seniority_pref = _safe_str(job_pref_input.get('seniority') or job_pref_input.get('level')) or 'Senior'
    areas_pref = _stringify_entries(
        job_pref_input.get('desired_roles') or job_pref_input.get('areas') or [],
        ('role', 'title', 'name', 'area', 'sector'),
    )
    area_str = ', '.join(areas_pref)
    if areas_pref:
        action_plan = ActionPlan(
            short_term=[f"Explorar oportunidades en {area_str}"],
            medium_term=[f"Desarrollar habilidades para rol {seniority_pref or 'Senior'}"],
            long_term=[f"Alcanzar posición {seniority_pref or 'Senior'} en {area_str}"],
        )
    else:
        action_plan = ActionPlan(
            short_term=[
                "Actualizar CV con información más detallada",
                "Crear perfil en LinkedIn",
                "Identificar 3-5 empresas objetivo",
            ],
            medium_term=[
                "Completar formación en habilidades técnicas",
                "Ampliar red profesional",
                "Preparar portfolio de proyectos",
            ],
            long_term=[
                "Desarrollar especialización técnica",
                "Buscar oportunidades de liderazgo",
                "Considerar certificaciones profesionales",
            ],
        )
    
    default_platforms = ["LinkedIn", "InfoJobs", "Indeed", "Stack Overflow Jobs"]
    cv_tips = (cv_analysis or {}).get('corrections', [
        "Usar palabras clave específicas del sector",
        "Incluir logros cuantificables",
        "Destacar proyectos relevantes",
    ])
    preferred_platforms_raw = (
        job_pref_input.get('preferred_platforms')
        or job_pref_input.get('preferredPlatforms')
        or job_pref_input.get('platforms')
        or job_pref_input.get('recommended_platforms')
        or []
    )
    recommended_platforms = _stringify_entries(preferred_platforms_raw) or default_platforms
    job_search_advice = JobSearchAdvice(
        cv_optimization=cv_tips,
        letters_portfolio="Destacar proyectos relevantes en la carta de presentación",
        recommended_platforms=recommended_platforms,
        networking="Participar en comunidades online" if work_mode_pref.lower() == 'remoto' else "Participar en meetups y grupos profesionales online",
        interview_tips="Preparar respuestas STAR y practicar presentación de proyectos",
    )

    productivity_tools = software_details or ["Trello", "Notion", "Google Calendar"]
    job_search_tools = recommended_platforms if recommended_platforms else ["LinkedIn", "Glassdoor", "Resume.io"]
    useful_tools = UsefulTools(
        productivity=productivity_tools,
        job_search=job_search_tools,
        learning=["Coursera", "edX", "Platzi", "Udemy"],
        accessibility=["Microsoft Immersive Reader", "Grammarly", "ColorZilla"],
    )
    
    # Crear roles sugeridos a partir de las preferencias cuando existan
    preferred_roles = areas_pref
    suggested_roles = []
    for role in preferred_roles:
        suggested_roles.append(
            SuggestedRole(
                role=role,
                reason='Basado en preferencias del usuario',
                seniority=seniority_pref or 'Junior',
                remote_viable=(work_mode_pref.lower() == 'remoto'),
            )
        )
    if not suggested_roles:
        suggested_roles = [
            SuggestedRole(
                role='Desarrollador Junior',
                reason='Perfil adecuado para roles de entrada con potencial de crecimiento',
                seniority='Junior',
                remote_viable=True,
            )
        ]

    ideal_work_environment_parts = []
    if work_mode_pref:
        ideal_work_environment_parts.append('Modalidad preferida: ' + work_mode_pref)
    if areas_pref:
        ideal_work_environment_parts.append('Áreas de interés: ' + ', '.join(areas_pref))
    ideal_work_environment = '. '.join(ideal_work_environment_parts) if ideal_work_environment_parts else 'Entorno inclusivo con oportunidades de aprendizaje y crecimiento profesional. Preferencia por empresas que valoren el desarrollo continuo.'

    
    location_pref_value = _safe_str(job_pref_input.get('location'))
    if not location_pref_value and personal_data.location != "No especificado":
        location_pref_value = personal_data.location
    has_cert_source = job_pref_input.get('hasDisabilityCert')
    if has_cert_source is None:
        has_cert_source = job_pref_input.get('has_disability_cert')
    if has_cert_source is None:
        has_cert_source = personal_data.disability_certificate

    job_pref_model = JobPreferences(
        location=location_pref_value,
        work_mode=work_mode_pref,
        areas=areas_pref,
        preferred_platforms=recommended_platforms if recommended_platforms else [],
        seniority=seniority_pref,
        has_disability_cert=_normalize_bool(has_cert_source),
    )

    return NewReportSchema(
        summary=f"Informe de empleabilidad para {full_name}",
        personal_data=personal_data,
        profile_summary=cv_analysis.get('summary', 'Perfil profesional con potencial de desarrollo. Se recomienda fortalecer habilidades técnicas específicas y experiencia práctica.') if cv_analysis else 'Perfil profesional con potencial de desarrollo. Se recomienda fortalecer habilidades técnicas específicas y experiencia práctica.',
        cv_summary=cv_summary_markdown,
        cv_details=cv_details,
        strengths=strengths,
        soft_skills=formatted_soft_skills,
        improvement_areas=improvement_areas,
        cv_analysis=cv_analysis_data,
        ideal_work_environment=ideal_work_environment,
        suggested_roles=suggested_roles,
        action_plan=action_plan,
        job_search_advice=job_search_advice,
        job_preferences=job_pref_model,
        useful_tools=useful_tools,
        employability_score=employability_score,
        completed_games=[],
        final_message=f"{full_name}, tu perfil muestra un excelente potencial para el desarrollo profesional. Enfócate en construir experiencia práctica y desarrollar habilidades técnicas específicas. La constancia y el aprendizaje continuo serán tus mejores aliados en la búsqueda de empleo.",
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
        try:
            score_int = int(score)
        except Exception:
            score_int = 0
        # Ajustar análisis del CV basado en la puntuación
        if score_int >= 80:
            default_report.cv_analysis.structure_score = 5
            default_report.cv_analysis.coherence_score = 5
        elif score_int >= 60:
            default_report.cv_analysis.structure_score = 4
            default_report.cv_analysis.coherence_score = 4
        elif score_int >= 40:
            default_report.cv_analysis.structure_score = 3
            default_report.cv_analysis.coherence_score = 3
        else:
            default_report.cv_analysis.structure_score = 2
            default_report.cv_analysis.coherence_score = 2

        default_report.employability_score = score_int

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

    job_pref_input = job_preferences.copy() if isinstance(job_preferences, dict) else {}
    
    # Crear áreas de mejora a partir del análisis del CV cuando sea posible
    if cv_analysis and (cv_analysis.get('corrections') or cv_analysis.get('reordering_suggestions')):
        improvement_areas = [
            {'area': c, 'reason': 'Corrección sugerida'} for c in cv_analysis.get('corrections', [])
        ] + [
            {'area': s, 'reason': 'Sugerencia de reordenamiento'} for s in cv_analysis.get('reordering_suggestions', [])
        ]
        if not improvement_areas:
            improvement_areas = []
    else:
        improvement_areas = [
            {'area': 'Experiencia técnica', 'reason': 'Necesita más práctica en tecnologías específicas'},
            {'area': 'Métricas de logros', 'reason': 'Faltan resultados cuantificables'},
        ]

    # Crear plan de acción basándose en preferencias cuando existan
    work_mode_pref = _safe_str(job_pref_input.get('workMode') or job_pref_input.get('work_mode'))
    seniority_pref = _safe_str(job_pref_input.get('seniority') or job_pref_input.get('level')) or 'Senior'
    areas_pref = _stringify_entries(
        job_pref_input.get('desired_roles') or job_pref_input.get('areas') or [],
        ('role', 'title', 'name', 'area', 'sector'),
    )
    area_str = ', '.join(areas_pref)
    if areas_pref:
        action_plan = {
            'short_term': [f"Explorar oportunidades en {area_str}"],
            'medium_term': [f"Desarrollar habilidades para rol {seniority_pref or 'Senior'}"],
            'long_term': [f"Alcanzar posición {seniority_pref or 'Senior'} en {area_str}"],
        }
    else:
        action_plan = {
            'short_term': [
                'Actualizar CV con información más detallada',
                'Crear perfil en LinkedIn',
                'Identificar 3-5 empresas objetivo',
            ],
            'medium_term': [
                'Completar formación en habilidades técnicas',
                'Ampliar red profesional',
                'Preparar portfolio de proyectos',
            ],
            'long_term': [
                'Desarrollar especialización técnica',
                'Buscar oportunidades de liderazgo',
                'Considerar certificaciones profesionales',
            ],
        }
    
    # Crear análisis del CV basado en los datos de entrada
   
    cv_analysis_data = {
        'structure': cv_analysis.get('structure', 'regular') if cv_analysis else 'regular',
        'coherence': cv_analysis.get('coherence', 'regular') if cv_analysis else 'regular',
        'feedback': cv_analysis.get('feedback', 'CV analizado con limitaciones') if cv_analysis else 'CV analizado con limitaciones',
        'summary': cv_analysis.get('summary', '') if cv_analysis else '',
        'experience': cv_analysis.get('experience', []) if cv_analysis else [],
        'education': cv_analysis.get('education', []) if cv_analysis else [],
        'software': cv_analysis.get('software', []) if cv_analysis else [],
    }
    cv_details_input = (cv_analysis or {}).get('cv_details') if isinstance((cv_analysis or {}).get('cv_details'), dict) else {}
    experience_input = (
        cv_details_input.get('experience')
        or (cv_analysis or {}).get('experience')
        or (cv_analysis or {}).get('experience_detailed')
        or []
    )
    education_input = (
        cv_details_input.get('education')
        or (cv_analysis or {}).get('education')
        or (cv_analysis or {}).get('education_detailed')
        or []
    )
    language_input = (
        cv_details_input.get('languages')
        or (cv_analysis or {}).get('languages')
        or (cv_analysis or {}).get('idiomas')
        or []
    )
    tools_input = (
        cv_details_input.get('tools')
        or (cv_analysis or {}).get('tools')
        or (cv_analysis or {}).get('software')
        or (cv_analysis or {}).get('skills')
        or []
    )

    cv_details = {
        'experience': _stringify_entries(
            experience_input,
            (
                'title', 'role', 'position', 'company', 'organization', 'employer', 'location', 'start_date', 'end_date', 'duration', 'description'
            ),
        ),
        'education': _stringify_entries(
            education_input,
            (
                'degree', 'title', 'program', 'area', 'institution', 'school', 'location', 'start_date', 'end_date', 'graduation_year', 'description'
            ),
        ),
        'languages': _stringify_entries(
            language_input,
            (
                'name', 'language', 'level', 'certification'
            ),
        ),
        'tools': _stringify_entries(
            tools_input,
            (
                'name', 'tool', 'technology', 'level', 'category'
            ),
        ),
    }
    # Crear consejos de búsqueda y herramientas útiles
    preferred_platforms_raw = (
        job_pref_input.get('preferred_platforms')
        or job_pref_input.get('preferredPlatforms')
        or job_pref_input.get('platforms')
        or job_pref_input.get('recommended_platforms')
        or []
    )
    recommended_platforms = _stringify_entries(preferred_platforms_raw) or ['LinkedIn', 'Indeed']
    cv_tips = (cv_analysis or {}).get('corrections') or ['gestión', 'coordinación', 'liderazgo']
    job_search_advice = {
        'cv_optimization': cv_tips,
        'letters_portfolio': 'Destacar proyectos relevantes',
        'recommended_platforms': recommended_platforms,
        'networking': 'Participar en comunidades online' if work_mode_pref.lower() == 'remoto' else 'Asistir a eventos locales',
        'interview_tips': 'Preparar ejemplos de proyectos relevantes',
    }

    productivity_entries = cv_details['tools'] or [
        str(item) for item in ((cv_analysis or {}).get('software') or ['Excel', 'Google Sheets']) if item
    ]
    useful_tools = {
        'productivity': productivity_entries,
        'job_search': recommended_platforms,
        'learning': ['Coursera', 'Udemy'],
        'accessibility': ['Microsoft Immersive Reader', 'Grammarly', 'ColorZilla'],
    }
    
    # Crear roles sugeridos a partir de preferencias de trabajo
    preferred_roles = areas_pref
    suggested_roles = []
    for role in preferred_roles:
        suggested_roles.append({
            'role': role,
            'reason': 'Basado en preferencias del usuario',
            'seniority': seniority_pref or 'Junior',
            'remote_viable': (work_mode_pref.lower() == 'remoto')
        })
    if not suggested_roles:
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
    
    location_pref_value = _safe_str(job_pref_input.get('location'))
    has_cert_source = job_pref_input.get('hasDisabilityCert')
    if has_cert_source is None:
        has_cert_source = job_pref_input.get('has_disability_cert')
    job_pref_export = JobPreferences(
        location=location_pref_value,
        work_mode=work_mode_pref,
        areas=areas_pref,
        preferred_platforms=recommended_platforms if recommended_platforms else [],
        seniority=seniority_pref,
        has_disability_cert=_normalize_bool(has_cert_source),
    ).dict()

    return {
        'softSkills': formatted_soft_skills,
        'improvement_areas': improvement_areas,
        'action_plan': action_plan,
        'cv_analysis': cv_analysis_data,
        'cv_details': cv_details,
        'job_search_advice': job_search_advice,
        'useful_tools': useful_tools,
        'suggested_roles': suggested_roles,
        'completed_games': completed_games,
        'employabilityScore': 76,  # Score por defecto
        'level': 'Intermedio',
        'job_preferences': job_pref_export,
    }
