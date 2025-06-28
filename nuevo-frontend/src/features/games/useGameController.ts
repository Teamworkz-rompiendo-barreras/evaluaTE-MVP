// src/features/games/useGameController.ts
import React, { useState, useEffect, useCallback, useRef } from 'react'

export function useGameController(totalSteps: number, stepDuration: number = 30) {
  const [currentStep, setCurrentStep] = useState(0)
  const [timeLeft, setTimeLeft] = useState(stepDuration)
  const timerRef = useRef<number | undefined>(undefined)

  const goNext = useCallback(() => {
    setCurrentStep((s) => Math.min(s + 1, totalSteps - 1))
    setTimeLeft(stepDuration)
  }, [stepDuration, totalSteps])

  const goPrev = useCallback(() => {
    setCurrentStep((s) => Math.max(s - 1, 0))
    setTimeLeft(stepDuration)
  }, [])

  // Reiniciamos el tiempo cada vez que cambiamos de paso
  useEffect(() => {
    setTimeLeft(stepDuration)
  }, [currentStep, stepDuration])

  // Cuenta regresiva activa mientras no estemos en el último paso
  useEffect(() => {
    if (currentStep >= totalSteps - 1) return

    // Inicia el temporizador
    timerRef.current = window.setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          goNext()
          return stepDuration
        }
        return t - 1
      })
    }, 1000)

    // Limpieza
    return () => {
      if (timerRef.current !== undefined) {
        clearInterval(timerRef.current)
      }
    }
  }, [currentStep, goNext, stepDuration, totalSteps])

  return {
    currentStep,
    timeLeft,
    goNext,
    goPrev,
  }
}