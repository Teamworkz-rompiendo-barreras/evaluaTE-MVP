# backend/new_report_schema.py
# -*- coding: utf-8 -*-
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class CompetenciaDetalle(BaseModel):
    nombre: str = ""
    puntuacion: int = 0
    nivel: str = ""
    explicacion: str = ""

class GrupoCompetencias(BaseModel):
    categoria: str = ""
    competencias: List[CompetenciaDetalle] = Field(default_factory=list)

class Fortaleza(BaseModel):
    nombre: str = ""
    explicacion_practica: str = ""

class AreaMejora(BaseModel):
    nombre: str = ""
    porque_afecta: str = ""
    como_mejorar: str = ""
    acciones_concretas: List[str] = Field(default_factory=list)

class ValoracionesCV(BaseModel):
    formato: int = 0
    claridad: int = 0
    coherencia: int = 0
    info_clave: int = 0
    ortografia: int = 0

class AnalisisCVAvanzado(BaseModel):
    resumen: str = ""
    experiencia: List[str] = Field(default_factory=list)
    formacion: List[str] = Field(default_factory=list)
    idiomas: List[str] = Field(default_factory=list)
    software: List[str] = Field(default_factory=list)
    valoraciones: ValoracionesCV = Field(default_factory=ValoracionesCV)
    puntos_fuertes: List[str] = Field(default_factory=list)
    aspectos_mejorar: List[str] = Field(default_factory=list)
    ats_compatibilidad: int = 0
    ats_explicacion: str = ""

class RolRecomendado(BaseModel):
    titulo: str = ""
    nivel: str = ""
    modalidad: str = ""
    por_que_encaja: str = ""
    salario_orientativo: str = ""
    demanda_laboral: str = ""

class PlanAccionFases(BaseModel):
    dias_30: List[str] = Field(default_factory=list)
    dias_60: List[str] = Field(default_factory=list)
    dias_90: List[str] = Field(default_factory=list)

class Herramienta(BaseModel):
    nombre: str = ""
    para_que_sirve: str = ""

class ResultadoJuego(BaseModel):
    juego: str = ""
    que_mide: str = ""
    resultado: str = ""
    interpretacion: str = ""
    aplicacion_entrevista: str = ""

class Recurso(BaseModel):
    nombre: str = ""
    tipo: str = ""
    descripcion: str = ""

# ESQUEMA MAESTRO DE 16 PUNTOS (B2B Production Safe)
class NewReportSchema(BaseModel):
    datos_personales: Dict[str, str] = Field(default_factory=dict)
    resumen_ejecutivo: str = ""
    puntuacion_global: int = 0
    interpretacion_global: str = ""
    perfil_competencias: List[GrupoCompetencias] = Field(default_factory=list)
    fortalezas_principales: List[Fortaleza] = Field(default_factory=list)
    areas_mejora: List[AreaMejora] = Field(default_factory=list)
    analisis_cv: AnalisisCVAvanzado = Field(default_factory=AnalisisCVAvanzado)
    entornos_ideales: List[str] = Field(default_factory=list)
    roles_recomendados: List[RolRecomendado] = Field(default_factory=list)
    plan_accion: PlanAccionFases = Field(default_factory=PlanAccionFases)
    estrategia_busqueda: List[str] = Field(default_factory=list)
    herramientas_recomendadas: List[Herramienta] = Field(default_factory=list)
    resultados_juegos: List[ResultadoJuego] = Field(default_factory=list)
    recomendaciones_personalizadas: List[str] = Field(default_factory=list)
    recursos_adicionales: List[Recurso] = Field(default_factory=list)
    mensaje_final: str = ""

    # Fallbacks de seguridad por si FastAPI recibe basura antigua
    employability_score: int = 0
    cv_details: Dict[str, Any] = Field(default_factory=dict)
    job_preferences: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "ignore" # Instrucción estricta: Ignorar cualquier clave que no esté aquí

def convert_old_format_to_new(data: Dict[str, Any]) -> Dict[str, Any]:
    return data