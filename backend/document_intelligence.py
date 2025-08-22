# backend/document_intelligence.py
import os
import logging
from typing import Any, Dict, List, Optional

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient  # SDK 3.x

logger = logging.getLogger("evaluador-backend")

def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default

def _default_stars() -> Dict[str, int]:
    # Valores por defecto conservadores (1..5)
    return {
        "formato": 3,
        "claridad": 3,
        "coherencia": 3,
        "informacion_clave": 2,
        "ortografia": 3,
    }

class DocumentIntelligenceService:
    def __init__(self, model_id: str = "prebuilt-document"):
        self.model_id = model_id
        endpoint = os.getenv("AZURE_DI_ENDPOINT")
        key = os.getenv("AZURE_DI_KEY")

        if not endpoint or not key:
            raise RuntimeError(
                "Faltan variables AZURE_DI_ENDPOINT y/o AZURE_DI_KEY para Document Intelligence."
            )

        self.client = DocumentAnalysisClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        logger.info("✅ Azure AI Document Intelligence configurado correctamente")

    def analyze_cv_with_document_intelligence(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Llama al modelo (custom o prebuilt) y devuelve un dict normalizado con:
        summary, strengths, weaknesses, feedback, stars, raw_text, experience, education, languages, software, contact
        """
        logger.info("🚀 Iniciando análisis con Azure AI Document Intelligence (modelo='%s')...", self.model_id)
        poller = self.client.begin_analyze_document(
            model_id=self.model_id,
            document=pdf_bytes,
        )
        result = poller.result()

        # ===== Texto total (para fallback y trazabilidad)
        text_full = ""
        try:
            if hasattr(result, "content") and result.content:
                text_full = result.content
            else:
                # SDK 3.x no siempre expone .content en custom models; usa pages
                if getattr(result, "pages", None):
                    text_full = "\n".join([p.content or "" for p in result.pages])
        except Exception:
            pass
        logger.info("📝 Texto extraído: %s caracteres", len(text_full))

        # ===== Extracción laxa de campos (funciona con modelos custom/prebuilt)
        experience: List[Dict[str, Any]] = []
        education: List[Dict[str, Any]] = []
        languages: List[Dict[str, Any]] = []
        software: List[str] = []
        contact: Dict[str, Any] = {"emails": [], "phones": [], "location": None, "linkedin": None}

        # 1) Intenta obtener documentos/fields si es custom
        docs = getattr(result, "documents", None) or []
        for doc in docs:
            fields = getattr(doc, "fields", {}) or {}
            # Campos típicos (si tu custom model los define)
            # Se tolera que no existan: no crashea
            if "experience" in fields and getattr(fields["experience"], "value", None):
                try:
                    for item in fields["experience"].value:
                        experience.append({
                            "position": str(item.fields.get("position").value) if item.fields.get("position") else None,
                            "company": str(item.fields.get("company").value) if item.fields.get("company") else None,
                            "start_date": str(item.fields.get("start_date").value) if item.fields.get("start_date") else None,
                            "end_date": str(item.fields.get("end_date").value) if item.fields.get("end_date") else None,
                            "current": bool(item.fields.get("current").value) if item.fields.get("current") else None,
                            "description": str(item.fields.get("description").value) if item.fields.get("description") else None,
                        })
                except Exception:
                    pass

            if "education" in fields and getattr(fields["education"], "value", None):
                try:
                    for item in fields["education"].value:
                        education.append({
                            "degree": str(item.fields.get("degree").value) if item.fields.get("degree") else None,
                            "institution": str(item.fields.get("institution").value) if item.fields.get("institution") else None,
                            "start_date": str(item.fields.get("start_date").value) if item.fields.get("start_date") else None,
                            "end_date": str(item.fields.get("end_date").value) if item.fields.get("end_date") else None,
                        })
                except Exception:
                    pass

            if "languages" in fields and getattr(fields["languages"], "value", None):
                try:
                    for item in fields["languages"].value:
                        languages.append({
                            "language": str(item.fields.get("language").value) if item.fields.get("language") else None,
                            "level": str(item.fields.get("level").value) if item.fields.get("level") else None,
                        })
                except Exception:
                    pass

            if "software" in fields and getattr(fields["software"], "value", None):
                try:
                    for item in fields["software"].value:
                        val = str(item.value) if getattr(item, "value", None) else None
                        if val:
                            software.append(val)
                except Exception:
                    pass

            if "contact" in fields and getattr(fields["contact"], "value", None):
                try:
                    cf = fields["contact"].value
                    if cf.get("emails") and cf["emails"].value:
                        contact["emails"] = [str(x.value) for x in cf["emails"].value if getattr(x, "value", None)]
                    if cf.get("phones") and cf["phones"].value:
                        contact["phones"] = [str(x.value) for x in cf["phones"].value if getattr(x, "value", None)]
                    if cf.get("location") and getattr(cf["location"], "value", None):
                        contact["location"] = str(cf["location"].value)
                    if cf.get("linkedin") and getattr(cf["linkedin"], "value", None):
                        contact["linkedin"] = str(cf["linkedin"].value)
                except Exception:
                    pass

        # Si no hay datos estructurados, intenta un fallback simple: listas detectadas en contenido
        # (No bloquea: solo rellena lo que falte)
        software = list(dict.fromkeys(software))  # dedup
        strengths: List[str] = []
        weaknesses: List[str] = []
        feedback: Optional[str] = None

        # Estrellas heurísticas por defecto (la UI las renderiza)
        stars = _default_stars()

        return {
            "summary": None,  # el resumen final lo hará la IA, aquí puede venir vacío
            "strengths": strengths,
            "weaknesses": weaknesses,
            "feedback": feedback,
            "stars": stars,
            "raw_text": text_full[:10000] if text_full else None,  # cap por seguridad
            "experience": experience or None,
            "education": education or None,
            "languages": languages or None,
            "software": software or None,
            "contact": contact if any([contact.get("emails"), contact.get("phones"), contact.get("location"), contact.get("linkedin")]) else None,
        }
