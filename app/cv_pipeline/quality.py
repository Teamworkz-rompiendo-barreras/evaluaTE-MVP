from typing import Tuple


def cv_quality_ok(cv: dict) -> Tuple[bool, str]:
    char_count = int(cv.get("char_count", 0) or 0)
    exp = len(cv.get("experience", []) or [])
    edu = len(cv.get("education", []) or [])
    contact = (cv.get("contact") or {}) if isinstance(cv.get("contact"), dict) else {}
    has_contact = bool(contact.get("emails") or contact.get("phones"))

    if char_count < 500 and exp == 0 and edu == 0:
        return False, "Extracción insuficiente (texto muy escaso y sin experiencia/formación estructurada)."
    if not has_contact:
        return False, "No se detectó ningún dato de contacto."
    return True, ""


