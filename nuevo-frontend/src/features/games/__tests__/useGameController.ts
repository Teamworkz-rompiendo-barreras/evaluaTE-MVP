// src/features/games/useGameController.ts
import { useState, useCallback } from 'react'
import type { SoftSkillResult } from '@/types/skills'

interface GameDecision {
  sceneId: number
  stepIndex: number
  optionText: string
  isCorrect: boolean
  skillImpacts: Record<string, number>
  timestamp: string
}

export function useGameController() {
  const [currentStep, setCurrentStep] = useState<number>(0)
  const [choices, setChoices] = useState<GameDecision[]>([])
  const totalSteps = 5

  const nextStep = useCallback(() => {
    setCurrentStep(prev => Math.min(prev + 1, totalSteps))
  }, [])

  const prevStep = useCallback(() => {
    setCurrentStep(prev => Math.max(prev - 1, 0))
  }, [])

  const resetGame = useCallback(() => {
    setCurrentStep(0)
    setChoices([])
  }, [])

  const makeChoice = useCallback((choice: GameDecision) => {
    setChoices(prev => [...prev, choice])
  }, [])

  const getSkillScores = useCallback(() => {
    const scores: Record<string, number> = {}

    choices.forEach(choice => {
      Object.entries(choice.skillImpacts).forEach(([skill, value]) => {
        if (!scores[skill]) {
          scores[skill] = 0
        }
        scores[skill] += value
      })
    })

    Object.keys(scores).forEach(skill => {
      scores[skill] = Number((scores[skill] / Math.max(choices.length, 1)).toFixed(2))
    })

    return scores
  }, [choices])

  const completed = currentStep >= totalSteps

  const progress = Math.round((currentStep / totalSteps) * 100)

  return {
    currentStep,
    choices,
    nextStep,
    prevStep,
    resetGame,
    makeChoice,
    getSkillScores,
    completed,
    progress,
  }
}