
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
        "experience": ["Desarrollador Senior en TechCorp (2020-2023)"],
        "education": ["Ingeniería Informática"],
        "languages": [{"language": "Inglés", "level": "C1"}],
        "software": ["Python", "Django"],
        "profile": "Desarrollador backend experimentado."
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
        assert "PROMPT MAESTRO" in prompt, "Missing title in prompt"
        assert "Juan Pérez" in prompt, "Candidate name missing"
        assert "Liderazgo" in prompt, "Soft skill missing"
        assert "Ingeniería Informática" in prompt, "Education missing"
        assert "ESTRUCTURA OBLIGATORIA DEL INFORME" in prompt, "JSON structure instructions missing"
        
        print("✅ Prompt structure validation passed.")
        
    except Exception as e:
        print(f"ERROR generating prompt: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prompt_generation()
