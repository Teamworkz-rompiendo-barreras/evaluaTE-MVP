// src/features/games/useGameController.ts
import { useState, useEffect, useCallback } from 'react';

export function useGameController(totalSteps: number) {
  const [currentStep, setCurrentStep] = useState(0);
  const [timeLeft, setTimeLeft] = useState(30); // por ejemplo, 30s por paso

  // Arranca el temporizador cada vez que cambie el paso
  useEffect(() => {
    setTimeLeft(30);
    const timer = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(timer);
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [currentStep]);

  const goNext = useCallback(() => {
    setCurrentStep((s) => Math.min(s + 1, totalSteps - 1));
  }, [totalSteps]);

  const goPrev = useCallback(() => {
    setCurrentStep((s) => Math.max(s - 1, 0));
  }, []);

  return { currentStep, timeLeft, goNext, goPrev };
}
