// src/features/games/useGameController.ts

// …
import { useState, useEffect, useCallback, useRef } from 'react';

export function useGameController(totalSteps: number, stepDuration = 30) {
  const [currentStep, setCurrentStep] = useState(0);
  const [timeLeft, setTimeLeft]     = useState(stepDuration);
  // Inicializamos timerRef a undefined y permitimos que sea number | undefined
  const timerRef = useRef<number | undefined>(undefined);

  const goNext = useCallback(() => {
    setCurrentStep(s => Math.min(s + 1, totalSteps - 1));
    setTimeLeft(stepDuration);
  }, [stepDuration, totalSteps]);

  const goPrev = useCallback(() => {
    setCurrentStep(s => Math.max(s - 1, 0));
    setTimeLeft(stepDuration);
  }, [stepDuration]);

  // Reiniciamos contador al cambiar de paso
  useEffect(() => {
    setTimeLeft(stepDuration);
  }, [currentStep, stepDuration]);

  // Efecto de cuenta atrás
  useEffect(() => {
    if (currentStep >= totalSteps - 1) return; // no contamos si es último paso

    // arrancamos el intervalo
    timerRef.current = window.setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          goNext();
          return stepDuration;
        }
        return t - 1;
      });
    }, 1000);

    // limpieza al desmontar o cambiar de paso
    return () => {
      if (timerRef.current !== undefined) {
        clearInterval(timerRef.current);
      }
    };
  }, [currentStep, goNext, stepDuration, totalSteps]);

  return { currentStep, timeLeft, goNext, goPrev };
}

