
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.prompt_config import PromptConfig
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
    from prompt_config import PromptConfig

def test_prompt_generation():
    print("Testing Gemini Prompt Generation...")
    
    # Mock Data matching the expected input defined in prompt_config.py
    candidate_data = {
        "fullName": "Juan Pérez",
        "location": "Madrid",
        "email": "juan@example.com",
        "phone": "600123456",
        "hasDisabilityCertificate": False
    }
    
    soft_skills_data = [
        {"skill": "Liderazgo", "score": 85, "level": "alto"},
        {"skill": "Comunicación", "score": 80, "level": "medio"}
    ]
    
    cv_data = {
        "contact": {"name": "Juan"},
        "experiencia": [{"rol": "Desarrollador Senior", "empresa": "TechCorp", "fecha_inicio": "2020", "fecha_fin": "2023"}],
        "educacion": [{"titulo": "Ingeniería Informática", "institucion": "UPM", "fecha_inicio": "2015", "fecha_fin": "2019"}],
        "idiomas": [{"language": "Inglés", "level": "C1"}],
        "habilidades_detectadas": ["Python", "Django"],
        "resumen_profesional": "Desarrollador backend experimentado."
    }
    
    job_preferences_data = {
        "desired_roles": ["Backend Developer", "Tech Lead"],
        "desired_sectors": ["Tecnología", "Fintech"],
        "work_modes": ["Remoto", "Híbrido"],
        "availability": "Inmediata",
        "relocation": False
    }
    
    employability_score = 82
    level = "alto"
    completed_games = ["Liderazgo 360", "Logic Master"]
    languages_data = [{"language": "Inglés", "level": "C1"}]
    
    full_raw_text = "Juan Pérez\nDesarrollador Backend\nExperiencia en TechCorp..."

    try:
        prompt = PromptConfig.get_employability_report_prompt(
            candidate_data=candidate_data,
            soft_skills_data=soft_skills_data,
            cv_data=cv_data,
            job_preferences_data=job_preferences_data,
            employability_score=employability_score,
            level=level,
            completed_games=completed_games,
            languages_data=languages_data,
            full_raw_text=full_raw_text
        )
        
        print("Prompt Generated Successfully!")
        print("-" * 50)
        print(prompt[:500] + "...") # Print first 500 chars
        print("-" * 50)
        
        # Validation checks
        assert "Juan Pérez" in prompt, "Candidate name missing"
        assert "Liderazgo" in prompt, "Soft skill missing"
        assert "Desarrollador Senior" in prompt, "Experience missing"
        assert "Ingeniería Informática" in prompt, "Education missing"
        assert "Backend Developer" in prompt, "Preferred role missing"
        assert "resumen_ejecutivo" in prompt, "JSON schema missing"
        
        print("OK - Prompt structure validation passed.")
        
    except Exception as e:
        print(f"ERROR generating prompt: {e}")
        import traceback
        traceback.print_exc()


def test_prompt_remote_restriction_and_alternatives():
    candidate_data = {"fullName": "Laura Gómez"}
    soft_skills_data = [{"skill": "Creatividad", "score": 92, "level": "alto"}]
    cv_data = {"raw_text": "Maquilladora freelance, beauty content creator, formación de peluquería y maquillaje."}
    job_preferences_data = {
        "desired_roles": ["Maquilladora"],
        "workMode": "remoto",
        "areas": ["Belleza", "Cosmética"]
    }

    prompt = PromptConfig.get_employability_report_prompt(
        candidate_data=candidate_data,
        soft_skills_data=soft_skills_data,
        cv_data=cv_data,
        job_preferences_data=job_preferences_data,
        employability_score=70,
        level="medio",
        completed_games=[],
        languages_data=[],
        lowest_skills_str="Comunicación oral",
    )

    assert "Maquilladora" in prompt
    assert "remoto" in prompt.lower()
    assert "inviable" in prompt.lower()
    assert "alternativa" in prompt.lower() or "pivote" in prompt.lower()
    assert "Profesora online de maquillaje" in prompt or "profesora online" in prompt.lower()
    assert "formación" in prompt.lower()


def test_prompt_uses_areas_as_role_when_desired_roles_missing():
    candidate_data = {"fullName": "Laura Gómez"}
    soft_skills_data = [{"skill": "Creatividad", "score": 92, "level": "alto"}]
    cv_data = {"raw_text": "Maquilladora freelance, beauty content creator, formación de peluquería y maquillaje."}
    job_preferences_data = {
        "areas": ["Maquilladora"],
        "workMode": "remoto",
        "needs": []
    }

    prompt = PromptConfig.get_employability_report_prompt(
        candidate_data=candidate_data,
        soft_skills_data=soft_skills_data,
        cv_data=cv_data,
        job_preferences_data=job_preferences_data,
        employability_score=70,
        level="medio",
        completed_games=[],
        languages_data=[],
        lowest_skills_str="Comunicación oral",
    )

    assert "Maquilladora" in prompt
    assert "remoto" in prompt.lower()
    assert "inviable" in prompt.lower()


def test_cv_analysis_fallback_when_model_returns_empty_section():
    from backend.cv_analyzer import _enforce_business_rules

    payload = {"analisis_cv": {}}
    fixed = _enforce_business_rules(payload)

    assert fixed["analisis_cv"]["resumen"]
    assert fixed["analisis_cv"]["puntos_fuertes"]
    assert fixed["analisis_cv"]["aspectos_mejorar"]
    assert fixed["analisis_cv"]["valoraciones"]["formato"] >= 1
    assert fixed["analisis_cv"]["ats_compatibilidad"] >= 0


def test_api_key_rotation_config():
    from backend.env_loader import get_gemini_api_keys, load_backend_env
    import os

    load_backend_env()
    keys = get_gemini_api_keys()
    assert len(keys) >= 2, "Debe haber varias claves de Gemini configuradas para fallback"
    assert keys[0] == (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))


def test_api_keys_are_loaded_from_backend_env_when_process_env_is_empty(monkeypatch):
    import os
    from backend.env_loader import get_gemini_api_keys

    for key_name in ["GOOGLE_API_KEY", "GEMINI_API_KEY", "GEMINI_KEY_1", "GEMINI_KEY_2"]:
        monkeypatch.delenv(key_name, raising=False)

    keys = get_gemini_api_keys()
    assert keys, "Debe resolver al menos una clave desde backend/.env cuando el entorno está vacío"
    assert all(key.startswith("AIza") or key.startswith("AQ.") for key in keys) 


if __name__ == "__main__":
    test_prompt_generation()
    test_prompt_remote_restriction_and_alternatives()
    test_cv_analysis_fallback_when_model_returns_empty_section()
    test_api_key_rotation_config()
