// src/features/games/useLogger.ts
import { v4 as uuidv4 } from 'uuid' // Para generar ID único de sesión

// Tipos esperados para los logs
interface BaseLog {
  timestamp: string
  gameId: number
  userId?: string
  sessionId: string
}

interface GameStepLog extends BaseLog {
  stepIndex: number
  optionIndex: number | null
  timeSpent: number
  usedHelp: boolean
  emotionalResponse: string | null
}

interface SoftSkillUpdateLog extends BaseLog {
  skill: string
  level: 'Bajo' | 'Medio' | 'Alto'
  confidence: number
}

interface FinalGameLog extends BaseLog {
  totalScore: number
  softSkills: SoftSkillResult[]
  stepsCompleted: number
  retries: number
}

// Hook principal
export function useLogger(userId?: string) {
  const sessionId = uuidv4()

  const logStep = async (payload: {
    gameId: number
    stepIndex: number
    optionIndex: number
    timeSpent: number
    usedHelp: boolean
    emotionalResponse: string | null
  }) => {
    const logData: GameStepLog = {
      ...payload,
      timestamp: new Date().toISOString(),
      sessionId,
      userId: userId || 'anonymous',
    }

    try {
      await fetch('/api/logs/step', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logData),
      })
    } catch (error) {
      console.error('Error registrando log de paso:', error)
    }
  }

  const logSoftSkill = async (payload: {
    gameId: number
    skill: string
    level: 'Bajo' | 'Medio' | 'Alto'
    confidence: number
  }) => {
    const logData: SoftSkillUpdateLog = {
      ...payload,
      timestamp: new Date().toISOString(),
      sessionId,
      userId: userId || 'anonymous',
    }

    try {
      await fetch('/api/logs/skill', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logData),
      })
    } catch (error) {
      console.error('Error registrando habilidad blanda:', error)
    }
  }

  const logFinalGame = async (gameId: number, softSkills: SoftSkillResult[]) => {
    const finalLog: FinalGameLog = {
      timestamp: new Date().toISOString(),
      gameId,
      sessionId,
      userId: userId || 'anonymous',
      softSkills: softSkills,
      stepsCompleted: softSkills.length,
      retries: 0, // Ajusta esto según tus datos reales
      totalScore: Math.round(
        softSkills.reduce((acc, s) => acc + s.confidence * 100, 0) / softSkills.length
      ),
    }

    try {
      await fetch('/api/logs/game-complete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(finalLog),
      })
    } catch (error) {
      console.error('Error registrando fin del juego:', error)
    }
  }

  return {
    logStep,
    logSoftSkill,
    logFinalGame,
  }
}