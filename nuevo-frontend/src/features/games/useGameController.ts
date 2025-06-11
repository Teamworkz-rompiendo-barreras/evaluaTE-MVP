import { useState, useEffect } from 'react'

export function useGameController(totalSteps: number) {
  const [currentStep, setStep] = useState(0)
  const [timeLeft, setTimeLeft] = useState(60) // segs

  useEffect(() => {
    const timer = setInterval(() => setTimeLeft(prev => prev - 1), 1000)
    return () => clearInterval(timer)
  }, [])

  const goNext = () => {
    if (currentStep < totalSteps - 1) setStep(s => s + 1)
  }

  return { currentStep, timeLeft, goNext }
}
