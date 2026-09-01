import os, sys, requests
from dotenv import load_dotenv

load_dotenv(r'C:\evaluaTE-MVP-main\backend\.env')
sys.path.insert(0, r'C:\evaluaTE-MVP-main\backend')
import cv_analyzer

assert 'gemini-3.6-flash' not in cv_analyzer.FALLBACK_MODELS, cv_analyzer.FALLBACK_MODELS
assert 'gemini-1.5-flash' in cv_analyzer.FALLBACK_MODELS, cv_analyzer.FALLBACK_MODELS
assert all(model in cv_analyzer.SUPPORTED_GEMINI_MODELS for model in cv_analyzer.FALLBACK_MODELS), cv_analyzer.FALLBACK_MODELS

payload = {
    'model': os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b'),
    'messages': [
        {'role': 'system', 'content': 'Responde solo JSON con {"status":"OK"}.'},
        {'role': 'user', 'content': 'Prueba'}
    ],
    'temperature': 0,
    'max_tokens': 64,
}
response = requests.post(
    'https://api.groq.com/openai/v1/chat/completions',
    headers={'Authorization': 'Bearer ' + os.getenv('GROQ_API_KEY'), 'Content-Type': 'application/json'},
    json=payload,
    timeout=90,
)
print('FALLBACK_MODELS=', cv_analyzer.FALLBACK_MODELS)
print('GROQ_STATUS=', response.status_code)
print('GROQ_BODY=', response.text[:400])
assert response.status_code == 200, response.text[:500]
