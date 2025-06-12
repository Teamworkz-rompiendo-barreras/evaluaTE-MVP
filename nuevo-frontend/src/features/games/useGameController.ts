// src/features/games/useGameController.ts
import { useState, useEffect, useRef } from 'react'

export function useGameController(stepsCount: number) {
  const [currentStep, setCurrentStep] = useState(0)
  const [timeLeft, setTimeLeft] = useState(60)
  const timerRef = useRef<NodeJS.Timeout | null>(null)

  // Reinicia el temporizador cada vez que cambias de step
  useEffect(() => {
    setTimeLeft(60)
    if (timerRef.current) clearInterval(timerRef.current)
    timerRef.current = setInterval(() => {
      setTimeLeft((t) => (t > 0 ? t - 1 : 0))
    }, 1000)
    return () => clearInterval(timerRef.current!)
  }, [currentStep, stepsCount])

  const goNext = () => {
    if (currentStep < stepsCount - 1) {
      setCurrentStep((s) => s + 1)
    }
  }
  const goPrev = () => {
    if (currentStep > 0) {
      setCurrentStep((s) => s - 1)
    }
  }

  return { currentStep, timeLeft, goNext, goPrev }
}
