# backend/prompt_config.py
# Configuración centralizada de prompts para EvaluaTE (Refactorizado P0)

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

class PromptConfig:
    """Configuración centralizada de prompts para el sistema EvaluaTE."""

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
        analysis_block: str = "",
        full_raw_text: str = "",
        is_multimodal: bool = False,
    ) -> str:
        """
        Genera el prompt maestro para el informe de empleabilidad completo.
        Implementa lógica de:
        - Schema estricto en Español.
        - Inyección dinámica de preferencias (Habilidades Transferibles).
        - Validación cruzada (CV vs Minijuegos).
        """
        
        # 1. Preparar datos del Candidato y Preferencias
        raw_name = candidate_data.get("fullName", "")
        full_name = raw_name if raw_name and raw_name not in ("Candidato", "Usuario") else ""
        
        # Preferencias obligatorias
        prefs = job_preferences_data or {}
        pref_role = ", ".join(prefs.get('desired_roles', [])) or "No especificado"
        pref_sector = ", ".join(prefs.get('desired_sectors', [])) or "No especificado"
        pref_modality = ", ".join(prefs.get('work_modes', [])) or "No especificado"
        pref_availability = prefs.get('availability', 'No especificada')
        
        # 2. Preparar datos del CV
        if is_multimodal:
            experience_text = "(Ver archivo adjunto - Extraer visualmente)"
            education_text = "(Ver archivo adjunto - Extraer visualmente)"
            cv_profile = "(Ver archivo adjunto)"
            cv_context_block = """
        **DATOS DEL CV:**
        El CV se adjunta como archivo PDF. DEBES LEERLO VISUALMENTE.
        Extrae la experiencia, educación y habilidades directamente del documento para generar el reporte.
            """
        else:
            # El cv_data viene del nuevo cv_analyzer que usa keys en español
            cv_exp = cv_data.get("experiencia", [])
            cv_edu = cv_data.get("educacion", [])
            cv_skills = cv_data.get("habilidades_detectadas", [])
            cv_langs = cv_data.get("idiomas", [])
            cv_profile = cv_data.get("resumen_profesional", "No consta")
            
            # Formatear experiencia para el prompt
            exp_text_list = []
            for e in cv_exp:
                if isinstance(e, dict):
                    row = f"- {e.get('rol', 'Rol?')} en {e.get('empresa', 'Empresa?')} ({e.get('fecha_inicio','?')} - {e.get('fecha_fin','?')})"
                    if e.get('descripcion'): row += f": {e.get('descripcion')}"
                    exp_text_list.append(row)
            experience_text = "\n".join(exp_text_list) if exp_text_list else "No consta experiencia."

            # Formatear educación
            edu_text_list = []
            for e in cv_edu:
                if isinstance(e, dict):
                    edu_text_list.append(f"- {e.get('titulo', '')} en {e.get('institucion', '')} ({e.get('fecha_inicio','')} - {e.get('fecha_fin','')})")
            education_text = "\n".join(edu_text_list) if edu_text_list else "No consta formación."
            
            cv_context_block = f"""
        **DATOS DEL CV:**
        - Resumen: {cv_profile}
        - Experiencia: 
        {experience_text}
        - Formación:
        {education_text}
            """
        
        # Soft Skills (Minijuegos)
        soft_skills_text = "\n".join([f"- {s.get('skill')}: {s.get('score')}/100 ({s.get('level')})" for s in soft_skills_data])
        
        # Lógica de Validación Cruzada
        cross_validation_instruction = """
        **REGLA DE VALIDACIÓN CRUZADA (CV vs JUEGOS):**
        Analiza la coherencia entre el perfil 'duro' del CV y el perfil 'blando' de los juegos (Soft Skills).
        - Si el CV dice 'CEO/Líder' pero en Soft Skills tiene 'Liderazgo: Bajo', GENERA un comentario diplomático en 'resumen_ejecutivo' y 'areas_mejora' explicando esta discrepancia.
        - Si el CV es junior pero tiene Soft Skills muy altas, destácalo como "Alto Potencial".
        """

        # Lógica de Preferencias Dinámicas (Habilidades Transferibles)
        preference_instruction = f"""
        **REGLA DE INYECCIÓN DE PREFERENCIAS:**
        El candidato DESEA trabajar como: **{pref_role}**.
        El candidato PREFIERE modalidad: **{pref_modality}**.
        
        TU ANÁLISIS DEBE CENTRARSE EN SU VIABILIDAD PARA **{pref_role}**, aunque su CV sea de otra cosa.
        - Si su experiencia NO encaja directo, BUSCA **HABILIDADES TRANSFERIBLES**.
        - Ejemplo: Si es "Camarero" y busca ser "Ventas", destaca "Trato al cliente" y "Gestión de presión".
        - NO le digas simplemente "Tu perfil es de Camarero". Dile "Para ser Ventas, capitaliza tu experiencia en trato al cliente...".
        """

        # Prompt Maestro
        nombre_placeholder = (
            "<NOMBRE COMPLETO DEL CANDIDATO - EXTRAER DEL CV ADJUNTO>"
            if is_multimodal else (full_name or "<Nombre del candidato>")
        )
        candidato_label = nombre_placeholder if is_multimodal else (full_name or "el candidato")

        prompt = f"""
        # ROL: ORIENTADOR LABORAL EXPERTO (IA)
        Analiza el perfil del candidato para generar un informe de empleabilidad estratégica.

        ## INPUTS
        **CANDIDATO:** {candidato_label}
        **PREFERENCIA ROL:** {pref_role}
        **PREFERENCIA SECTOR:** {pref_sector}
        **MODALIDAD:** {pref_modality}

        **RESULTADOS SOFT SKILLS (JUEGOS):**
        {soft_skills_text}

        {cv_context_block}

        **TEXTO RAW COMPLETO (Contexto Visual):**
        {str(full_raw_text)[:6000]}

        ---

        ## INSTRUCCIONES DE RAZONAMIENTO
        1. {cross_validation_instruction}
        2. {preference_instruction}
        3. **Estilo:** Profesional, motivador, empático pero realista. Idioma: Español (España).

        ---

        ## FORMATO DE SALIDA (JSON ESTRICTO)
        Debes devolver UNICAMENTE un objeto JSON que valide contra este esquema exacto (15 secciones).
        Si falta información, usa "No consta" o arrays vacíos, NO cortes el JSON.

        {{
          "datos_personales": {{ "nombre": "{nombre_placeholder}", "email": "<email del CV o No consta>", "telefono": "<teléfono del CV o No consta>", "ubicacion": "<ciudad/país del CV>", "discapacidad": "<SOLO 'Sí' si el CV indica EXPLÍCITAMENTE un certificado de discapacidad (ej. 'Certificado de discapacidad 33%'); en cualquier otro caso, incluso si se menciona inclusión/diversidad sin más, escribe 'No consta'>" }},
          "experiencia": [
            {{ "rol": "<cargo>", "empresa": "<empresa>", "periodo": "<fecha inicio - fecha fin>", "descripcion": "<logros principales en 1 línea>" }}
          ],
          "educacion": [
            {{ "titulo": "<titulación>", "institucion": "<centro>", "periodo": "<años>" }}
          ],
          "idiomas": [
            {{ "idioma": "<nombre>", "nivel": "<nivel certificado o estimado>" }}
          ],
          "habilidades": ["<herramienta o tecnología 1>", "<herramienta 2>"],
          "resumen_ejecutivo": "Texto narrativo potente (5-6 líneas). Resume quién es, sus soft skills clave, su viabilidad para el rol deseado ({pref_role}) y su valor diferencial.",
          "resumen_cv": "Resumen técnico de su trayectoria, formación y herramientas detectadas.",
          "analisis_foda": {{
            "fortalezas_clave": ["F1 (Score/100): Explicación", "F2..."],
            "areas_mejora": ["D1: Diagnóstico -> Acción", "D2..."]
          }},
          "analisis_detallado_cv": "Análisis párrafo a párrafo de la calidad de su CV. ¿Vende bien sus logros? ¿Estructura clara?",
          "entornos_ideales": ["Remoto/Híbrido (basado en pref)", "Cultura startup/corp...", "Entornos colaborativos..."],
          "roles_sugeridos": [
            {{ "rol": "{pref_role} (Role Principal)", "ajuste": "Alto/Medio/Bajo", "justificacion": "..." }},
            {{ "rol": "Rol Alternativo 1", "ajuste": "...", "justificacion": "Basado en tus skills transferibles..." }}
          ],
          "plan_accion": {{
            "pasos": ["Corto plazo: ... (máx 15 palabras)", "Corto plazo: ...", "Medio plazo: ...", "Medio plazo: ...", "Largo plazo: ...", "Largo plazo: ..."],
            "herramientas": ["Trello", "LinkedIn", "Canva..."],
            "lecturas": ["Libro X", "Blog Y", "Curso Z"]
          }},
          "optimizacion_cv": ["Sugerencia 1 (máx 15 palabras)", "Sugerencia 2", "Sugerencia 3"],
          "capitalizar_fortalezas": "Consejo estratégico sobre cómo usar sus puntos fuertes (Juegos + CV) para conseguir el puesto de {pref_role}.",
          "kit_busqueda": {{
            "frases_linkedin": {{
               "titular": "Ej: Especialista en {pref_role} | Habilidad 1 | Habilidad 2",
               "acerca_de": "Ej: Profesional orientada a {pref_role} con experiencia en..."
            }},
            "mensaje_reclutador": "Plantilla de mensaje para contactar recruiters solicitando puesto de {pref_role}..."
          }},
          "mensaje_final_azul": "Texto motivacional de cierre, inspirador y personalizado."
        }}
        """
        
        return prompt

    @staticmethod
    def get_report_schema() -> dict:
        """Retorna el esquema JSON estricto para validación (opcional, para uso en tests)."""
        return {
             "type": "object",
             "required": ["datos_personales", "resumen_ejecutivo", "analisis_foda", "roles_sugeridos", "mensaje_final_azul"],
             "properties": {
                 "datos_personales": {"type": "object"},
                 "resumen_ejecutivo": {"type": "string"},
                 "analisis_foda": {"type": "object"},
                 "roles_sugeridos": {"type": "array"}
             }
        }
