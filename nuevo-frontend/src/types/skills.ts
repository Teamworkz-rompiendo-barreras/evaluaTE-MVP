// src/types/skills.ts

/**
 * Análisis del CV cargado por el usuario
 */
export interface CvAnalysis {
  /**
   * Puntaje global del CV (0-100)
   */
  score: number

  /**
   * Puntos fuertes identificados
   */
  strengths: string[]

  /**
   * Áreas a mejorar
   */
  weaknesses: string[]

  /**
   * Recomendaciones generales del análisis
   */
  feedback?: string

  /**
   * Logs técnicos del análisis del CV
   */
  rawLog?: Record<string, any>
}

/**
 * Resultado de evaluación de habilidades blandas
 */
export interface SoftSkillResult {
  /**
   * Nombre de la habilidad (ej: Toma de decisiones)
   */
  skill: string

  /**
   * Nivel evaluado (Bajo / Medio / Alto)
   */
  level: 'Bajo' | 'Medio' | 'Alto'

  /**
   * Porcentaje de confianza (0.3 - 1)
   */
  confidence: number

  /**
   * Descripción del nivel alcanzado
   */
  feedback?: string

  /**
   * Registro de interacciones durante esta evaluación
   */
  interactions: UserDecision[]
}

/**
 * Preferencias laborales del candidato
 */
export interface JobPreference {
  /**
   * Sectores o áreas de interés
   */
  areas: string[]

  /**
   * Necesidades específicas
   */
  needs: string[]

  /**
   * Modo de trabajo preferido
   */
  workMode?: 'remoto' | 'presencial' | 'híbrido'

  /**
   * Disponibilidad horaria
   */
  availability?: 'mañana' | 'tarde' | 'completa'

  /**
   * ¿Está dispuesto a mudarse si es necesario?
   */
  willingToRelocate: boolean

  /**
   * ¿Tiene certificado de discapacidad?
   */
  hasDisabilityCert: boolean

  /**
   * Configuración de accesibilidad usada durante la gamificación
   */
  accessibilitySettings?: AccessibilitySettings
}

/**
 * Configuración de accesibilidad según elecciones del usuario
 */
export interface AccessibilitySettings {
  easyReadingMode: boolean
  audioAssistiveMode: boolean
  showPictograms: boolean
  contrastLevel: 'normal' | 'alto' | 'muy-alto'
}

/**
 * Informe final de empleabilidad
 */
export interface EmployabilityReport extends JobPreference {
  /**
   * ID único del usuario
   */
  userId: string

  /**
   * Nombre completo del candidato
   */
  fullName: string

  /**
   * Habilidades blandas evaluadas
   */
  softSkills: SoftSkillResult[]

  /**
   * Puntaje global de empleabilidad (0-100)
   */
  employabilityScore: number

  /**
   * Análisis del CV cargado
   */
  cvAnalysis?: CvAnalysis

  /**
   * Fecha de creación del informe
   */
  createdAt: string

  /**
   * Última fecha de modificación
   */
  updatedAt: string

  /**
   * Juegos completados hasta ahora
   */
  completedGames: number[]

  /**
   * Nivel de empleabilidad (bajo/media/alta)
   */
  level: 'Baja empleabilidad' | 'Empleabilidad media' | 'Alta empleabilidad'

  /**
   * Recomendaciones personalizadas
   */
  recommendations: {
    roles: string[]
    resources: string[]
    cvImprovements: string[]
    nextSteps: string[]
  }

  /**
   * Logs completos del sistema para IA
   */
  logs: GameDecisionLog[]
}

/**
 * Registro de decisión tomada por el usuario
 */
export interface UserDecision {
  sceneId: number
  stepIndex: number
  optionText: string
  isCorrect: boolean
  skillImpacts: Record<string, number>
  timestamp: string
  userAgent: string
  screenResolution: string
}

/**
 * Log detallado de juego para IA
 */
export interface GameDecisionLog {
  sceneId: number
  decisions: UserDecision[]
  totalSteps: number
  totalTime: number
  averageConfidence: number
  emotionalTrend: ('positivo' | 'neutro' | 'negativo')[]
  accessibilityUsed: boolean
  accessibilitySettings?: AccessibilitySettings
}