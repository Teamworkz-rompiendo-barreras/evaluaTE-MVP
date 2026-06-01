from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class DatosPersonales(BaseModel):
    nombre: str
    ubicacion: str
    contacto: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    discapacidad: Optional[str] = None
    linkedin: Optional[str] = None

class AnalisisFODA(BaseModel):
    fortalezas_clave: List[str]
    areas_mejora: List[str]

class RolSugerido(BaseModel):
    rol: str
    ajuste: str
    justificacion: str

class PlanAccion(BaseModel):
    pasos: List[str]
    herramientas: List[str]
    lecturas: List[str]

class KitBusqueda(BaseModel):
    frases_linkedin: Dict[str, str]
    mensaje_reclutador: str

class NewReportSchema(BaseModel):
    # Campos obligatorios del Schema P0 (Español)
    datos_personales: DatosPersonales
    resumen_ejecutivo: str
    resumen_cv: str
    analisis_foda: AnalisisFODA
    analisis_detallado_cv: str
    entornos_ideales: List[str]
    roles_sugeridos: List[RolSugerido]
    plan_accion: PlanAccion
    capitalizar_fortalezas: str
    kit_busqueda: KitBusqueda
    mensaje_final_azul: str
    
    # Campos opcionales / legacy que main.py podría inyectar
    employability_score: Optional[int] = 0
    level: Optional[str] = "medio"
    soft_skills: Optional[List[Dict[str, Any]]] = []
    
    # Permite campos extra si la IA alucina alguno menor, para no romper
    class Config:
        extra = "ignore"


def convert_old_format_to_new(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza el JSON del informe IA al formato que espera NewReportSchema."""
    def _str(v, default=""):
        return str(v) if v else default

    def _list(v, default=None):
        return v if isinstance(v, list) else (default or [])

    def _dict(v, default=None):
        return v if isinstance(v, dict) else (default or {})

    dp_raw = _dict(data.get("datos_personales"))
    datos_personales = {
        "nombre": _str(dp_raw.get("nombre") or dp_raw.get("name"), "Candidato"),
        "ubicacion": _str(dp_raw.get("ubicacion") or dp_raw.get("location")),
        "contacto": _str(dp_raw.get("contacto") or dp_raw.get("email")),
        "email": _str(dp_raw.get("email")),
        "telefono": _str(dp_raw.get("telefono") or dp_raw.get("phone")),
        "linkedin": _str(dp_raw.get("linkedin")),
    }

    foda_raw = _dict(data.get("analisis_foda"))
    analisis_foda = {
        "fortalezas_clave": _list(foda_raw.get("fortalezas_clave") or foda_raw.get("fortalezas"), ["No evaluado"]),
        "areas_mejora": _list(foda_raw.get("areas_mejora") or foda_raw.get("debilidades"), ["No evaluado"]),
    }

    plan_raw = _dict(data.get("plan_accion"))
    plan_accion = {
        "pasos": _list(plan_raw.get("pasos"), ["Revisar el informe"]),
        "herramientas": _list(plan_raw.get("herramientas"), []),
        "lecturas": _list(plan_raw.get("lecturas"), []),
    }

    kit_raw = _dict(data.get("kit_busqueda"))
    kit_busqueda = {
        "frases_linkedin": _dict(kit_raw.get("frases_linkedin"), {}),
        "mensaje_reclutador": _str(kit_raw.get("mensaje_reclutador")),
    }

    roles_raw = _list(data.get("roles_sugeridos"))
    roles_sugeridos = [
        {
            "rol": _str(r.get("rol") if isinstance(r, dict) else ""),
            "ajuste": _str(r.get("ajuste") if isinstance(r, dict) else ""),
            "justificacion": _str(r.get("justificacion") if isinstance(r, dict) else ""),
        }
        for r in roles_raw
    ] or [{"rol": "No especificado", "ajuste": "medio", "justificacion": ""}]

    return {
        **data,
        "datos_personales": datos_personales,
        "resumen_ejecutivo": _str(data.get("resumen_ejecutivo")),
        "resumen_cv": _str(data.get("resumen_cv") or data.get("resumen_profesional")),
        "analisis_foda": analisis_foda,
        "analisis_detallado_cv": _str(data.get("analisis_detallado_cv") or data.get("analisis_cv")),
        "entornos_ideales": _list(data.get("entornos_ideales"), []),
        "roles_sugeridos": roles_sugeridos,
        "plan_accion": plan_accion,
        "capitalizar_fortalezas": _str(data.get("capitalizar_fortalezas")),
        "kit_busqueda": kit_busqueda,
        "mensaje_final_azul": _str(data.get("mensaje_final_azul")),
    }
