// src/types/game-scene.ts

import type { SoftSkillResult } from '@/types/skills'

/**
 * Una opción seleccionada por el usuario en una escena
 */
export interface SceneOption {
  text: string
  isCorrect: boolean
  skillImpact?: Record<string, number> // Impacto en habilidades blandas (ej: {'Toma de decisiones': 0.9})
  feedback?: string // Feedback tras elegir esta opción
}

/**
 * Paso o momento dentro de una escena
 */
export interface GameStep {
  text: string
  image?: string
  options: SceneOption[]
}

/**
 * Escena completa del minijuego
 */
export interface GameScene {
  id: number
  title: string
  steps: GameStep[]
}

/**
 * Respuesta del API al pedir una escena
 */
export interface GameSceneResponse {
  id: number
  title: string
  steps: GameStep[]
}

/**
 * Registro de decisión tomada por el usuario
 */
export interface UserDecision {
  sceneId: number
  stepIndex: number
  optionText: string
  timestamp: string
  isCorrect: boolean
  skillImpacts: Record<string, number>
}

/**
 * Historial de decisiones del usuario
 */
export interface UserDecisionHistory {
  decisions: UserDecision[]
  userId: string
  createdAt: string
  updatedAt: string
}