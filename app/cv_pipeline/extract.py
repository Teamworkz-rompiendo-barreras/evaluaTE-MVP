from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import fitz  # PyMuPDF
import re
import os


@dataclass
class CVExtraction:
    text: str
    char_count: int
    sections: Dict[str, Any]  # profile, experience, education, languages, skills, contact...
    source: str               # "native" | "azure_read" | "tesseract" | "none"
    metrics: Dict[str, Any]   # e.g., {"has_email": True, "phones": 1}


EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)


def _extract_native(pdf_bytes: bytes) -> Optional[CVExtraction]:
    try:
        text_parts: List[str] = []
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text_parts.append(page.get_text("text") or "")
        full = "\n".join(text_parts)
        return CVExtraction(
            text=full,
            char_count=len(full or ""),
            sections={},
            source="native",
            metrics={"has_email": bool(EMAIL_RE.search(full or ""))},
        )
    except Exception:
        return None


def _extract_azure_read(pdf_bytes: bytes, *, endpoint: str, key: str) -> Optional[CVExtraction]:
    # Usa Azure Document Intelligence: prebuilt-read/prebuilt-layout
    # Devuelve estructura similar a CVExtraction
    try:
        from azure.ai.formrecognizer import DocumentAnalysisClient  # type: ignore
        from azure.core.credentials import AzureKeyCredential  # type: ignore
    except Exception:
        return None

    endpoint = (endpoint or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT") or "").strip()
    key = (key or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY") or "").strip()
    if not endpoint or not key:
        return None

    try:
        client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        try:
            with open(tmp_path, "rb") as fh:
                try:
                    poller = client.begin_analyze_document("prebuilt-layout", fh)
                    result = poller.result()
                except Exception:
                    fh.seek(0)
                    poller = client.begin_analyze_document("prebuilt-read", fh)
                    result = poller.result()
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

        content = getattr(result, "content", "") or ""
        return CVExtraction(
            text=content,
            char_count=len(content),
            sections={},
            source="azure_read",
            metrics={"has_email": bool(EMAIL_RE.search(content))},
        )
    except Exception:
        return None


def _extract_tesseract(pdf_bytes: bytes) -> Optional[CVExtraction]:
    # Solo si empaquetas binario tesseract en tu imagen
    # En esta implementación MVP, devolvemos None para apoyarnos en Azure
    return None


def extract_cv(pdf_bytes: bytes, *, endpoint: str = "", key: str = "") -> CVExtraction:
    # Prioriza Azure si poco texto nativo
    native = _extract_native(pdf_bytes)
    if native and native.char_count >= 500:
        return native

    for fn in (
        lambda b: _extract_azure_read(b, endpoint=endpoint, key=key),
        lambda b: _extract_tesseract(b),
    ):
        res = fn(pdf_bytes)
        if res and res.char_count >= 500:
            return res

    # último recurso: devuelve lo mejor que tengas (aunque marque baja calidad)
    res = native or CVExtraction("", 0, {}, "none", {})
    return res


