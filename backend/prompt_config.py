# backend/prompt_config.py
from typing import Dict, List

class PromptConfig:
    """Configuración centralizada de Arquitectura Cognitiva B2B de Alta Fidelidad para EvalúaTE."""
    
    CATEGORY_ORDER = [
        "COMPETENCIAS COGNITIVAS",
        "COMPETENCIAS INTERPERSONALES/SOCIALES",
        "COMPETENCIAS INTRAPERSONALES/ADAPTATIVAS",
        "OTRAS COMPETENCIAS EVALUADAS",
    ]
    
    COMPETENCY_CATEGORIES = {
        "Toma de decisiones": "COMPETENCIAS COGNITIVAS",
        "Pensamiento analítico": "COMPETENCIAS COGNITIVAS",
        "Creatividad": "COMPETENCIAS COGNITIVAS",
        "Pensamiento Crítico": "COMPETENCIAS COGNITIVAS",
        "Influencia social": "COMPETENCIAS INTERPERSONALES/SOCIALES",
        "Empatía": "COMPETENCIAS INTERPERSONALES/SOCIALES",
        "Liderazgo": "COMPETENCIAS INTERPERSONALES/SOCIALES",
        "Curiosidad y aprendizaje": "COMPETENCIAS INTRAPERSONALES/ADAPTATIVAS",
        "Resiliencia y flexibilidad": "COMPETENCIAS INTRAPERSONALES/ADAPTATIVAS",
        "Autoconciencia": "COMPETENCIAS INTRAPERSONALES/ADAPTATIVAS",
    }

    @staticmethod
    def _group_soft_skills_by_category(soft_skills_data: list) -> str:
        buckets: Dict[str, list] = {cat: [] for cat in PromptConfig.CATEGORY_ORDER}
        for s in soft_skills_data or []:
            name = s.get("skill", "")
            category = PromptConfig.COMPETENCY_CATEGORIES.get(name, "OTRAS COMPETENCIAS EVALUADAS")
            buckets[category].append(s)
        
        lines = []
        for cat in PromptConfig.CATEGORY_ORDER:
            items = buckets[cat]
            if not items: 
                continue
            lines.append(f"{cat}:")
            for s in items:
                lines.append(f"- {s.get('skill', '')}: {s.get('score', 0)}/100 (Nivel: {s.get('level', '')})")
            lines.append("")
        return "\n".join(lines).strip()

    @staticmethod
    def _as_string_list(value) -> list:
        if value is None:
            return []
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        if isinstance(value, (list, tuple, set)):
            items = []
            for item in value:
                items.extend(PromptConfig._as_string_list(item))
            return items
        if isinstance(value, dict):
            return PromptConfig._as_string_list(list(value.values()))
        return [str(value)]

    @staticmethod
    def get_employability_report_prompt(
        candidate_data: dict,
        soft_skills_data: list,
        cv_data: dict,
        job_preferences_data: dict,
        employability_score: int,
        level: str,
        completed_games: list,
        languages_data: list,
        is_multimodal: bool = False,
        lowest_skills_str: str = "",
    ) -> str:
        raw_name = candidate_data.get("fullName", "")
        full_name = raw_name if raw_name and raw_name not in ("Candidato", "Usuario") else "el candidato"
        prefs = job_preferences_data or {}

        preferred_role_sources = [
            prefs.get('desired_roles'), prefs.get('desiredRoles'), prefs.get('role'),
            prefs.get('target_role'), prefs.get('job_title'), prefs.get('preferred_role'),
            prefs.get('roles'), prefs.get('areas'), prefs.get('sectors'), prefs.get('jobAreas')
        ]
        pref_roles = []
        for source in preferred_role_sources:
            for value in PromptConfig._as_string_list(source):
                item = str(value).strip()
                if item and item not in pref_roles:
                    pref_roles.append(item)
        pref_role = ", ".join(pref_roles) if pref_roles else "No especificado"

        modality_sources = [prefs.get('workMode'), prefs.get('work_mode'), prefs.get('modalidad'), prefs.get('mode'), prefs.get('working_mode')]
        pref_modality = next((str(v).strip() for v in modality_sources if str(v).strip()), 'No especificado')
        viability_note = (
            "El objetivo laboral indicado por el usuario tiene prioridad absoluta. Evalúa si es viable en la modalidad elegida. "
            "Si requiere presencia física y no puede ejecutarse en remoto, marca la viabilidad como NO REALIZABLE e INVIABLE en remoto y ofrece "
            "alternativas digitales del mismo sector. Ejemplos: maquilladora -> Profesora online de maquillaje, Asesora de belleza online, "
            "Creadora de contenido beauty, Comercial de cosmética digital. Si no tiene formación para ese pivote, recomienda formación específica y accesible."
        )
        
        grouped_skills_text = PromptConfig._group_soft_skills_by_category(soft_skills_data)
        games_text = "\n".join([str(g) for g in completed_games]) if completed_games else "Evaluación general de competencias completada"
        cv_text = cv_data.get("raw_text", "No se ha proporcionado texto explícito del CV.")

        prompt = f"""
# MISIÓN
Genera un informe ejecutivo de talento para {full_name}.

# DATOS
- Objetivo: {pref_role}
- Modalidad: {pref_modality}
- Nota global: {employability_score}/100
- Debilidad clave: {lowest_skills_str}
- CV:
\"\"\"
{cv_text}
\"\"\"
- Competencias:
{grouped_skills_text}
- Juegos:
{games_text}

# REGLAS OBLIGATORIAS
1. {viability_note}
2. Si el rol principal es inviable en remoto, explica por qué y ofrece un pivote realista del mismo sector. La alternativa debe ser clara y concreta: por ejemplo, 'Profesora online de maquillaje' o 'Asesora de belleza online'.
3. En 'roles_recomendados' incluye al menos dos alternativas viables; si es maquillaje, incluye 'Profesora online de maquillaje'.
4. Si el pivote exige formación, recomienda cursos reales y concretos en 'recursos_adicionales' y 'areas_mejora'.
5. Devuelve SOLO JSON con esta estructura:
{{
  "diagnostico_interno_oculto": {{"objetivo_real": "...", "viabilidad_objetivo": "...", "hipotesis_profesional": "..."}},
  "datos_personales": {{"Nombre": "{full_name}", "Modalidad": "{pref_modality}", "Email": "...", "Telefono": "...", "LinkedIn": "..."}},
  "resumen_ejecutivo": "...",
  "puntuacion_global": {employability_score},
  "interpretacion_global": "...",
  "perfil_competencias": [{{"categoria": "COMPETENCIAS COGNITIVAS", "competencias": [{{"nombre": "...", "puntuacion": 80, "nivel": "Alto", "explicacion": "..."}}]}}],
  "fortalezas_principales": [{{"nombre": "...", "explicacion_practica": "..."}}],
  "areas_mejora": [{{"nombre": "{lowest_skills_str}", "porque_afecta": "...", "como_mejorar": "PLAN DE CAPACITACIÓN INMEDIATA:", "acciones_concretas": ["...", "...", "..."]}}],
  "analisis_cv": {{"resumen": "...", "experiencia": ["..."], "formacion": ["..."], "idiomas": ["..."], "software": ["..."], "valoraciones": {{"formato": 4, "claridad": 4, "coherencia": 3, "info_clave": 4, "ortografia": 5}}, "puntos_fuertes": ["..."], "aspectos_mejorar": ["..."], "ats_compatibilidad": 65, "ats_explicacion": "..."}},
  "entornos_ideales": ["...", "..."],
  "roles_recomendados": [{{"titulo": "Profesora online de maquillaje", "nivel": "Junior/Mid", "modalidad": "Remoto", "por_que_encaja": "Justificación de encaje temporal: ...", "demanda_laboral": "ALTA"}}, {{"titulo": "Asesora de belleza online", "nivel": "Junior/Mid", "modalidad": "Remoto", "por_que_encaja": "Justificación de encaje temporal: ...", "demanda_laboral": "MEDIA-ALTA"}}],
  "plan_accion": {{"dias_30": ["Optimización del CV y perfil digital", "Formación inmediata del pivote", "Envío activo de candidaturas"], "dias_60": ["Curso específico", "Portfolio o contenidos", "Networking digital"], "dias_90": ["Consolidar oferta", "Establecer presencia online", "Revisar resultados"]}},
  "estrategia_busqueda": ["...", "...", "...", "...", "..."],
  "herramientas_recomendadas": [{{"nombre": "LinkedIn", "para_que_sirve": "..."}}],
  "resultados_juegos": [{{"juego": "...", "que_mide": "DIMENSIÓN: ...", "resultado": "...", "interpretacion": "Mapeo Psicométrico: ...", "aplicacion_entrevista": "Transferencia a Entrevista: ..."}}],
  "recomendaciones_personalizadas": ["...", "...", "...", "...", "..."],
  "recursos_adicionales": [{{"nombre": "Curso de maquillaje profesional", "tipo": "DESARROLLO DE HABILIDAD ESPECÍFICA", "descripcion": "..."}}, {{"nombre": "Marketing de belleza y contenidos online", "tipo": "FORMACIÓN HABILITANTE", "descripcion": "..."}}],
  "mensaje_final": "..."
}}
"""
        return prompt