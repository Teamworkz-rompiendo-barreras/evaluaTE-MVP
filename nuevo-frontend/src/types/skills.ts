// src/types/skills.ts

/**
 * Análisis del CV cargado por el usuario
 */
export interface CvAnalysis {
  score: number // Puntaje global del CV (0-100)
  strengths: string[] // Puntos fuertes identificados
  weaknesses: string[] // Áreas a mejorar
  feedback?: string // Recomendaciones generales
}

/**
 * Resultado de evaluación de habilidades blandas
 */
export interface SoftSkillResult {
  skill: string // Nombre de la habilidad (ej: Toma de decisiones)
  level: 'Bajo' | 'Medio' | 'Alto' // Nivel evaluado
  confidence: number // Porcentaje de confianza (0.3 - 1)
  feedback?: string // Descripción del nivel alcanzado
}

/**
 * Preferencias laborales del candidato
 */
export interface JobPreference {
  areas: string[]
  needs: string[]
  workMode?: 'remoto' | 'presencial' | 'híbrido'
  availability?: 'mañana' | 'tarde' | 'completa'
  willingToRelocate: boolean
  hasDisabilityCert: boolean
}

/**
 * Informe final de empleabilidad
 */
export interface EmployabilityReport {
  userId: string
  fullName: string
  softSkills: SoftSkillResult[]
  employabilityScore: number
  jobPreferences: JobPreference
  createdAt: string
  updatedAt: string
  completedGames: number[]
}