# backend/pii_masking.py
import re

def mask_pii_data(text: str, candidate_name: str) -> str:
    """
    Pipeline de desidentificación (Pseudonymization).
    Oculta PII crítico antes de enviar los datos al LLM.
    """
    if not text:
        return ""

    sanitized_text = text

    # 1. Enmascarar Emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    sanitized_text = re.sub(email_pattern, '[EMAIL_OCULTO]', sanitized_text)

    # 2. Enmascarar Teléfonos (Formatos internacionales y locales)
    phone_pattern = r'(?:\+?\d{1,3}[\s.-]?)?\(?\d{2,3}\)?[\s.-]?\d{3}[\s.-]?\d{2,4}'
    sanitized_text = re.sub(phone_pattern, '[TELÉFONO_OCULTO]', sanitized_text)

    # 3. Enmascarar DNI / NIE / Pasaportes (España)
    dni_pattern = r'\b(?:[XYZxyz]\d{7}[A-Za-z]|\d{8}[A-Za-z])\b'
    sanitized_text = re.sub(dni_pattern, '[ID_OCULTO]', sanitized_text)

    # 4. Enmascarar Nombre del Candidato (Case-insensitive)
    if candidate_name and candidate_name.lower() not in ["candidato", "usuario", ""]:
        # Escapar caracteres especiales del nombre para evitar inyecciones en la Regex
        escaped_name = re.escape(candidate_name.strip())
        name_pattern = re.compile(rf'\b{escaped_name}\b', re.IGNORECASE)
        sanitized_text = name_pattern.sub('[CANDIDATO]', sanitized_text)

    return sanitized_text