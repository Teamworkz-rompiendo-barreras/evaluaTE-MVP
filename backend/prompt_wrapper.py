# backend/prompt_wrapper.py
"""
Adaptador de puente entre la CLI de Promptfoo (Node.js) y la clase PromptConfig (Python).
Permite desestructurar el diccionario de variables 'vars' de forma segura.
"""
from prompt_config import PromptConfig

def generate_prompt(context):
    vars_dict = context.get('vars', {})
    
    candidate_data = vars_dict.get('candidate_data', {})
    soft_skills_data = vars_dict.get('soft_skills_data', [])
    cv_data = vars_dict.get('cv_data', {})
    job_preferences_data = vars_dict.get('job_preferences_data', {})
    employability_score = vars_dict.get('employability_score', 70)
    level = vars_dict.get('level', 'Medio')
    completed_games = vars_dict.get('completed_games', [])
    languages_data = vars_dict.get('languages_data', [])
    is_multimodal = vars_dict.get('is_multimodal', False)
    lowest_skills_str = vars_dict.get('lowest_skills_str', '')

    return PromptConfig.get_employability_report_prompt(
        candidate_data=candidate_data,
        soft_skills_data=soft_skills_data,
        cv_data=cv_data,
        job_preferences_data=job_preferences_data,
        employability_score=employability_score,
        level=level,
        completed_games=completed_games,
        languages_data=languages_data,
        is_multimodal=is_multimodal,
        lowest_skills_str=lowest_skills_str
    )