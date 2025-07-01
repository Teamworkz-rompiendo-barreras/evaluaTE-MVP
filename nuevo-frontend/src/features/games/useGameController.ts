// src/features/games/useGameController.ts
import React, { useState, useEffect, useCallback, useRef } from 'react'
import { useDispatch } from 'react-redux'

// Tipos compartidos
import type {
  GameStep,
  SceneOption,
} from '@/types/game-scene'

// Acciones desde Redux
import { unlockGame } from '@/features/progress/progressSlice'

export interface UseGameControllerProps {
  sceneId: number
  steps: GameStep[]
  initialStep?: number
  timePerStep?: number
}

export default function useGameController({
  sceneId,
  steps = [],
  initialStep = 0,
  timePerStep = 30,
}: UseGameControllerProps) {
  const dispatch = useDispatch()
  const [currentStep, setCurrentStep] = useState(initialStep)
  const [timeLeft, setTimeLeft] = useState(timePerStep)
  const [choices, setChoices] = useState<SceneOption[]>([])
  const [completed, setCompleted] = useState(false)
  const timerRef = useRef<number | undefined>(undefined)

  // Avanzar al siguiente paso
  const nextStep = useCallback(() => {
    if (currentStep < steps.length - 1) {
      setCurrentStep((prev) => prev + 1)
      setTimeLeft(timePerStep)
    } else {
      finishGame()
    }
  }, [currentStep, steps.length])

  // Retroceder al paso anterior
  const prevStep = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1)
      setTimeLeft(timePerStep)
    }
  }, [currentStep])

  // Registrar una elección del usuario
  const makeChoice = useCallback(
    (option: SceneOption) => {
      setChoices((prev) => [...prev, option])
      
      // Si es correcta, desbloqueamos el próximo juego
      if (option.isCorrect) {
        dispatch(unlockGame(sceneId))
      }

      nextStep()
    },
    [sceneId, nextStep]
  )

  // Finaliza el juego y genera puntaje
  const finishGame = useCallback(() => {
    setCompleted(true)
    setTimeLeft(0)
  }, [])

  // Reinicia el juego
  const resetGame = useCallback(() => {
    setCurrentStep(0)
    setTimeLeft(timePerStep)
    setChoices([])
    setCompleted(false)
  }, [timePerStep])

  // Reiniciar temporizador cuando cambia de paso
  useEffect(() => {
    setTimeLeft(timePerStep)
  }, [currentStep, timePerStep])

  // Inicia el temporizador
  useEffect(() => {
    if (completed || currentStep >= steps.length - 1) return

    timerRef.current = window.setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          nextStep()
          return timePerStep
        }
        return t - 1
      })
    }, 1000)

    return () => {
      if (timerRef.current !== undefined) {
        clearInterval(timerRef.current)
      }
    }
  }, [completed, currentStep, steps.length, timePerStep])

  return {
    currentStep,
    timeLeft,
    choices,
    completed,
    nextStep,
    prevStep,
    makeChoice,
    resetGame,
    progress: Math.round(((currentStep + 1) / steps.length) * 100),
  }
}