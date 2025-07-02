// src/features/games/__tests__/useGameController.test.tsx
import { renderHook, act } from '@testing-library/react';
import useGameController from '@/features/games/useGameController';

// Tipos desde tu proyecto
import type {
  GameScene,
  SceneOption,
  UserDecision,
} from '@/types/game-scene';

describe('useGameController', () => {
  const mockScene: GameScene = {
    id: 1,
    sceneId: 1, // Agregado sceneId
    title: 'Minijuego 1: La primera llamada',
    steps: [
      {
        text: 'Recibes una llamada inesperada. ¿Qué haces?',
        options: [
          {
            text: 'Respondes de inmediato',
            isCorrect: true,
            skillImpact: { 'Toma de decisiones': 0.9 },
            feedback: 'Buena toma de decisión. Has actuado con responsabilidad.',
          },
          {
            text: 'Pides tiempo para pensar',
            isCorrect: false,
            skillImpact: { 'Toma de decisiones': 0.5 },
            feedback: 'Has querido ayudar, pero es mejor asegurarse antes de actuar.',
          },
        ],
        timeLimit: 30, // Agregado timeLimit
      },
      {
        text: 'Demasiadas tareas. ¿Cómo las ordenas?',
        options: [
          {
            text: 'Según prioridad',
            isCorrect: true,
            skillImpact: { 'Resolución de problemas': 0.8 },
            feedback: 'Has organizado bien',
          },
          {
            text: 'Dejas algunas para después',
            isCorrect: false,
            skillImpact: { 'Gestión del tiempo': 0.4 },
            feedback: 'Evita dejar cosas pendientes si puedes',
          },
        ],
        timeLimit: 30, // Agregado timeLimit
      },
    ],
    softSkillsTracked: ['Toma de decisiones', 'Resolución de problemas'],
    accessibilityOptions: {
      showPictograms: true,
      audioAssistiveMode: true,
      contrastLevel: 'normal',
    },
  };

  it('debería iniciar correctamente con datos de escena', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));

    expect(result.current.currentStep).toBe(0);
    expect(result.current.timeLeft).toBe(30);
    expect(result.current.choices.length).toBe(0);
    expect(result.current.completed).toBe(false);
  });

  it('debería avanzar al siguiente paso', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));

    act(() => {
      result.current.nextStep();
    });

    expect(result.current.currentStep).toBe(1);
    expect(result.current.timeLeft).toBe(30);
    expect(result.current.progress).toBe(50);
  });

  it('debería retroceder al paso anterior', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));

    act(() => {
      result.current.nextStep();
      result.current.prevStep();
    });

    expect(result.current.currentStep).toBe(0);
    expect(result.current.timeLeft).toBe(30);
  });

  it('debería registrar una decisión del usuario', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));

    const option: SceneOption = {
      text: 'Respondes de inmediato',
      isCorrect: true,
      skillImpact: { 'Toma de decisiones': 0.9 },
      feedback: 'Buena toma de decisión',
    };

    act(() => {
      result.current.makeChoice(option);
      result.current.nextStep();
    });

    expect(result.current.choices.length).toBe(1);
    expect(result.current.choices[0].text).toBe('Respondes de inmediato');
  });

  it('debería completar el juego tras finalizar todos los pasos', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));

    act(() => {
      for (let i = 0; i < mockScene.steps.length; i++) {
        result.current.makeChoice(mockScene.steps[i].options[0]);
        if (i < mockScene.steps.length - 1) {
          result.current.nextStep();
        }
      }
    });

    expect(result.current.completed).toBe(true);
    expect(result.current.progress).toBe(100);
  });

  it('debería calcular puntaje promedio de habilidades blandas', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));

    const option1: SceneOption = {
      text: 'Respondes de inmediato',
      isCorrect: true,
      skillImpact: { 'Toma de decisiones': 0.9 },
      feedback: 'Muy buena opción',
    };

    const option2: SceneOption = {
      text: 'Según prioridad',
      isCorrect: true,
      skillImpact: { 'Resolución de problemas': 0.8 },
      feedback: 'Has organizado bien',
    };

    act(() => {
      result.current.makeChoice(option1);
      result.current.nextStep();
      result.current.makeChoice(option2);
    });

    const scores = result.current.getSkillScores();

    expect(scores['Toma de decisiones']).toBe(0.9);
    expect(scores['Resolución de problemas']).toBe(0.8);
  });

  it('debería reiniciar el juego correctamente', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));

    act(() => {
      result.current.nextStep();
      result.current.resetGame();
    });

    expect(result.current.currentStep).toBe(0);
    expect(result.current.choices).toEqual([]);
    expect(result.current.completed).toBe(false);
    expect(result.current.progress).toBe(0);
  });

  it('debería registrar decisiones del usuario con contexto completo', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));

    const option: SceneOption = {
      text: 'Respondes de inmediato',
      isCorrect: true,
      skillImpact: { 'Toma de decisiones': 0.9 },
      feedback: 'Muy buena opción',
    };

    act(() => {
      result.current.makeChoice(option);
    });

    expect(result.current.choices.length).toBe(1);
    expect(result.current.choices[0].isCorrect).toBe(true);
    expect(result.current.choices[0].userAgent).toBe(navigator.userAgent);
    expect(result.current.choices[0].screenResolution).toBe(`${window.innerWidth}x${window.innerHeight}`);
  });
});