// src/types/skills.ts

// Nivel de habilidad blanda evaluada por IA
export type SoftSkillLevel = 'Bajo' | 'Medio' | 'Alto'

// Una habilidad blanda evaluada
export interface SoftSkillResult {
  skill: string // nombre de la habilidad (ej: "Toma de decisiones")
  level: SoftSkillLevel // nivel de dominio
  confidence: number // puntuación de confianza: entre 0 y 1
}

// Resultado final de un minijuego
export interface GameResult {
  gameId: number
  softSkills: SoftSkillResult[]
  score: number // puntuación global del juego (ej: 85%)
  stepsCompleted: number
  timeSpent: number
  usedHelp: boolean
}

// Resultado global del usuario tras todos los juegos
export interface EmployabilityReport {
  userId: string
  cvAnalysis?: CvAnalysis
  softSkills: SoftSkillResult[]
  employabilityScore: number
  jobPreferences: JobPreference
  createdAt: string
}

// Análisis del CV
export interface CvAnalysis {
  score: number
  strengths: string[]
  weaknesses: string[]
  feedback?: string
}

// Preferencias laborales del usuario
export interface JobPreference {
  areas?: string[] // ej: ["Logística", "Atención al cliente"]
  needs?: string[] // ej: ["Trabajo en entorno tranquilo"]
  workMode?: 'remoto' | 'presencial' | 'híbrido'
  availability?: 'mañana' | 'tarde' | 'completa'
  startDate?: 'inmediata' | '15_días' | '1_mes' | 'más_de_1_mes'
  willingToRelocate: boolean
  hasDisabilityCert: boolean
}