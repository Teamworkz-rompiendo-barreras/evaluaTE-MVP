# backend/new_report_schema.py
from pydantic import BaseModel, Field

# --- FASE 1: ARQUITECTURA COGNITIVA (RAZONAMIENTO OCULTO) ---
class DiagnosticoInternoOculto(BaseModel):
    objetivo_real: str = Field(description="Análisis crudo de lo que busca el candidato.")
    nivel_empleabilidad_real: str = Field(description="Evaluación realista de su situación actual en el mercado.")
    fortalezas_clave: list[str] = Field(description="Fortalezas probadas con evidencia en el CV o juegos.")
    riesgos_y_bloqueos: list[str] = Field(description="Motivos reales por los que podrían descartar su perfil.")
    lagunas_formativas: list[str] = Field(description="Qué no sabe hacer y necesita aprender urgentemente.")
    viabilidad_objetivo: str = Field(description="¿Es viable su objetivo en la modalidad deseada? Si no, justifica el pivote digital sectorial.")
    hipotesis_profesional: str = Field(description="Modelo mental final que guiará TODO el informe. Única fuente de verdad.")

# --- COMPONENTES BASE ---
class DatosPersonales(BaseModel):
    Nombre: str
    Ubicacion: str
    Email: str
    Telefono: str
    LinkedIn: str

class ValoracionesCV(BaseModel):
    formato: int = Field(ge=1, le=5)
    claridad: int = Field(ge=1, le=5)
    coherencia: int = Field(ge=1, le=5)
    info_clave: int = Field(ge=1, le=5)
    ortografia: int = Field(ge=1, le=5)

class AnalisisCV(BaseModel):
    resumen: str = Field(description="Diagnóstico implacable y analítico sobre la calidad del documento. Mínimo 5 líneas.")
    experiencia: list[str]
    formacion: list[str]
    idiomas: list[str]
    software: list[str]
    valoraciones: ValoracionesCV
    puntos_fuertes: list[str] = Field(description="Array de puntos fuertes reales del CV.")
    aspectos_mejorar: list[str] = Field(description="Cita textualmente errores ortográficos o carencias críticas detectadas.")
    ats_compatibilidad: int = Field(ge=0, le=100)
    ats_explicacion: str

class CompetenciaDetalle(BaseModel):
    nombre: str
    puntuacion: int = Field(ge=0, le=100)
    nivel: str
    explicacion: str = Field(description="Análisis de 3 líneas. Qué significa, cómo se manifiesta en el trabajo y qué valor aporta.")

class CategoriaCompetencias(BaseModel):
    categoria: str
    competencias: list[CompetenciaDetalle]

class Fortaleza(BaseModel):
    nombre: str = Field(description="Ej: 'TOMA DE DECISIONES EFECTIVA'")
    explicacion_practica: str = Field(description="Justifica la fortaleza integrando sus puntuaciones altas de los juegos con experiencia del CV.")

class AreaMejora(BaseModel):
    nombre: str = Field(description="Ej: 'CURIOSIDAD Y APRENDIZAJE'")
    porque_afecta: str = Field(description="Explicación clínica de cómo esta carencia bloquea su objetivo profesional. Mínimo 3 líneas.")
    como_mejorar: str = Field(description="OBLIGATORIO usar exactamente el texto 'PLAN DE CAPACITACIÓN INMEDIATA:'.")
    acciones_concretas: list[str] = Field(description="Array de 3 acciones formativas inmediatas y específicas.")

class ResultadoJuego(BaseModel):
    juego: str
    que_mide: str = Field(description="Obligatorio iniciar con: 'DIMENSIÓN: [Explicación en mayúsculas de lo que mide]'.")
    resultado: str = Field(description="Puntuación o métrica cruda.")
    interpretacion: str = Field(description="Obligatorio iniciar con: 'Mapeo Psicométrico: [Análisis conductual profundo]'. Mínimo 4 líneas.")
    aplicacion_entrevista: str = Field(description="Obligatorio iniciar con: 'Transferencia a Entrevista: [Ejemplo práctico de defensa]'.")

class RolRecomendado(BaseModel):
    titulo: str = Field(description="Rol viable. Si el objetivo es imposible, propón alternativas viables (Pivote).")
    nivel: str = Field(description="Ej: 'Mid-level', 'Senior'")
    modalidad: str = Field(description="Ej: 'Remoto', 'Presencial'")
    por_que_encaja: str = Field(description="OBLIGATORIO comenzar con 'Justificación de encaje temporal: '. Explica por qué encaja.")
    demanda_laboral: str = Field(description="Indica exclusivamente: 'ALTA', 'MEDIA-ALTA', 'MEDIA' o 'BAJA'. PROHIBIDO SALARIOS.")

class PlanAccion(BaseModel):
    dias_30: list[str] = Field(description="Array de 3 acciones críticas urgentes. Incluir optimización de CV y envío activo de candidaturas.")
    dias_60: list[str] = Field(description="Array de 3 acciones de tracción (Certificaciones, networking).")
    dias_90: list[str] = Field(description="Array de 3 acciones de consolidación (Entrevistas, simulacros).")

class HerramientaRecomendada(BaseModel):
    nombre: str = Field(description="Ej: 'LinkedIn Learning / Coursera' o CRMs reales.")
    para_que_sirve: str = Field(description="Explicación específica de cómo esta herramienta soluciona un problema.")

class RecursoAdicional(BaseModel):
    nombre: str = Field(description="Nombre exacto de un CURSO o CERTIFICACIÓN real.")
    tipo: str = Field(description="Obligatorio usar SOLO: 'FORMACIÓN HABILITANTE', 'DESARROLLO DE HABILIDAD ESPECÍFICA' o 'FORMACIÓN COMPLEMENTARIA'.")
    descripcion: str = Field(description="Justificación profunda de por qué necesita este recurso basándose en sus lagunas.")

# --- FASE 3: CHUNKS PARA MAP-REDUCE ---
class Chunk1Base(BaseModel):
    datos_personales: DatosPersonales
    resumen_ejecutivo: str = Field(description="Análisis premium detallado. Mínimo 100 palabras. Si el objetivo remoto inicial es inviable, justificar pivote aquí.")
    puntuacion_global: int = Field(ge=0, le=100)
    interpretacion_global: str = Field(description="Evaluación conectada directamente a su viabilidad de mercado. Mínimo 5 líneas.")
    analisis_cv: AnalisisCV

class Chunk2Competencias(BaseModel):
    perfil_competencias: list[CategoriaCompetencias]
    fortalezas_principales: list[Fortaleza]
    areas_mejora: list[AreaMejora]
    resultados_juegos: list[ResultadoJuego]

class Chunk3Accion(BaseModel):
    entornos_ideales: list[str] = Field(description="Array de 4 descripciones de cultura empresarial y modalidad de trabajo ideal.")
    roles_recomendados: list[RolRecomendado]
    plan_accion: PlanAccion
    estrategia_busqueda: list[str] = Field(description="Array de 5 tácticas específicas y desarrolladas (Networking, Portfolio, etc).")
    herramientas_recomendadas: list[HerramientaRecomendada]
    recomendaciones_personalizadas: list[str] = Field(description="Ajustes inmediatos. Array de 5 acciones contundentes.")
    recursos_adicionales: list[RecursoAdicional]
    mensaje_final: str = Field(description="Veredicto de consultoría formal, analítico y profesional. Inspira confianza pero sé realista.")