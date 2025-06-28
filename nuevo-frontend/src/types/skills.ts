// src/types/skills.ts

// Nivel de habilidad blanda evaluada por IA
export type SoftSkillLevel = 'Bajo' | 'Medio' | 'Alto'

// Habilidad blanda básica
export interface SoftSkillResult {
  skill: string // nombre de la habilidad (ej: "Toma de decisiones")
  level: SoftSkillLevel // nivel de dominio
  confidence: number // puntuación de confianza: entre 0 y 1
}

// Tipos de habilidades blandas según documento técnico
export type SoftSkillType =
  | 'Toma de decisiones'
  | 'Resolución de problemas'
  | 'Trabajo en equipo'
  | 'Gestión emocional'
  | 'Comunicación'
  | 'Curiosidad y aprendizaje continuo'
  | 'Creatividad'
  | 'Flexibilidad'
  | 'Pensamiento crítico'
  | 'Autonomía'
  | 'Empatía'
  | 'Gestión del tiempo'
  | 'Autoconciencia'
  | 'Autorregulación emocional'
  | 'Regulación emocional'
  | 'Aprendizaje operativo'
  | 'Priorización laboral'
  | 'Adaptabilidad cognitiva'
  | 'Resiliencia'
  | 'Iniciativa personal'

// Resultado final de un minijuego
export interface GameResult {
  gameId: number
  gameName: string
  softSkills: SoftSkillResult[]
  score: number // puntuación global del juego (ej: 85%)
  stepsCompleted: number
  timeSpent: number
  usedHelp: boolean
  retries: number
  emotionalResponse?: string // respuesta emocional implícita
}

// Informe final del usuario tras todos los juegos
export interface EmployabilityReport {
  userId: string
  fullName?: string
  cvAnalysis?: CvAnalysis
  softSkills: SoftSkillResult[]
  employabilityScore: number
  jobPreferences: JobPreference
  createdAt: string
  updatedAt?: string
  completedGames: number[]
}

// Análisis del CV
export interface CvAnalysis {
  score: number
  strengths: string[]
  weaknesses: string[]
  feedback?: string
  sections: CvSection[] // ej: experiencia, formación, idiomas
  flags: CvFlag[] // ej: formato desactualizado, falta de objetivos claros
}

// Secciones del CV analizadas
export interface CvSection {
  title: string
  content: string
  relevance?: number // 0 - 100
  flagged: boolean
}

// Flags detectados en el CV
export interface CvFlag {
  reason: string
  severity: 'low' | 'medium' | 'high'
  suggestions: string[]
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

// Datos de sesión para IA
export interface SessionData {
  sessionId: string
  logs: LogEntry[]
  softSkills: SoftSkillResult[]
  gameResults: GameResult[]
  cvAnalysis?: CvAnalysis
}

// Entrada de log de sesión
export interface LogEntry {
  timestamp: string
  gameId: number
  stepIndex: number
  optionIndex: number
  timeSpent: number
  usedHelp: boolean
  emotionalResponse: string | null
}

// Evaluación de soft skill basada en múltiples fuentes
export interface SkillEvaluation {
  skill: SoftSkillType
  level: SoftSkillLevel
  confidence: number
  sources: {
    gameIds: number[]
    weightedScores: Record<number, number> // { gameId: score }
  }
}