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
