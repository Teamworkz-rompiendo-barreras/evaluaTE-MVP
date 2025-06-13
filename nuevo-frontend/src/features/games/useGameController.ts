// src/features/games/useGameController.ts
import { useState, useEffect, useCallback, useRef } from 'react';

export function useGameController(totalSteps: number, stepDuration = 30) {
  // totalSteps: número de pantallas de este minijuego
  // stepDuration: segundos que dura cada paso antes de forzar avanzar

  const [currentStep, setCurrentStep] = useState(0);
  const [timeLeft, setTimeLeft] = useState(stepDuration);
  const timerRef = useRef<number>();

  // Avanza manualmente
  const goNext = useCallback(() => {
    setCurrentStep(s => Math.min(s + 1, totalSteps - 1));
    setTimeLeft(stepDuration);
  }, [stepDuration, totalSteps]);

  // Retrocede manualmente
  const goPrev = useCallback(() => {
    setCurrentStep(s => Math.max(s - 1, 0));
    setTimeLeft(stepDuration);
  }, [stepDuration]);

  // Cada vez que cambie currentStep, reiniciamos el temporizador
  useEffect(() => {
    setTimeLeft(stepDuration);
  }, [currentStep, stepDuration]);

  // Efecto que cuenta atrás
  useEffect(() => {
    // si ya es el último paso, no iniciamos cronómetro
    if (currentStep >= totalSteps - 1) return;

    // decremento cada segundo
    timerRef.current = window.setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          // al llegar a 0, avanzamos de paso
          goNext();
          return stepDuration;
        }
        return t - 1;
      });
    }, 1000);

    // limpieza al desmontar o cambiar de paso
    return () => {
      clearInterval(timerRef.current);
    };
  }, [currentStep, goNext, stepDuration, totalSteps]);

  return { currentStep, timeLeft, goNext, goPrev };
}
