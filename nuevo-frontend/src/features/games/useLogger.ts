// src/features/games/useLogger.ts
import { v4 as uuidv4 } from 'uuid' // Para generar ID único de sesión

// Tipos esperados para los logs
// (Si StepLog no se usa, eliminarlo)

interface SoftSkillLog {
  gameId: number
  skillName: string
  confidence: number
  level: 'Bajo' | 'Medio' | 'Alto'
}

export const useLogger = () => {
  const sessionId = uuidv4()

  const logStep = async (stepData: {
    gameId: number;
    stepIndex: number;
    optionIndex: number;
    timeSpent: number;
    usedHelp: boolean;
    emotionalResponse: string | null;
  }) => {
    try {
      const response = await fetch('/api/logs/step', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...stepData,
          sessionId,
          timestamp: new Date().toISOString(),
        }),
      })

      if (!response.ok) {
        // console.warn('Error al guardar log de paso')
      }
    } catch {
      // console.warn('Error de red al guardar log de paso')
    }
  }

  const logSoftSkill = async (skillData: SoftSkillLog) => {
    try {
      const response = await fetch('/api/logs/soft-skill', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...skillData,
          sessionId,
          timestamp: new Date().toISOString(),
        }),
      })

      if (!response.ok) {
        // console.warn('Error al guardar log de habilidad blanda')
      }
    } catch {
      // console.warn('Error de red al guardar log de habilidad blanda')
    }
  }

  const logFinalGame = async (gameId: number, softSkills: unknown[]) => {
    try {
      const response = await fetch('/api/logs/final-game', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gameId,
          softSkills,
          totalScore: Math.round(
            softSkills.reduce((acc: number, s: unknown) => acc + ((s as { confidence?: number }).confidence || 0) * 100, 0) / softSkills.length
          ),
        }),
      })

      if (!response.ok) {
        // console.warn('Error al guardar resultado final del juego')
      }
    } catch {
      // console.warn('Error de red al guardar resultado final del juego')
    }
  }

  return {
    logStep,
    logSoftSkill,
    logFinalGame,
  }
}