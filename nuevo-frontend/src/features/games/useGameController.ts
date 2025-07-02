// nuevo-frontend/src/features/games/__tests__/useGameController.test.ts

import { renderHook, act } from '@testing-library/react-hooks';
import { useGameController } from '../useGameController';
import { GameScene, SceneOption } from '@/types/game-scene';
import { UserDecision } from '@/types/skills';

describe('useGameController', () => {
  const mockScene: GameScene = {
    id: 1,
    sceneId: 1, // Agregado
    title: 'Minijuego 1',
    description: 'Descripción del minijuego 1',
    steps: [
      {
        id: 1,
        description: 'Paso 1',
        options: [
          { id: 1, text: 'Opción 1' },
          { id: 2, text: 'Opción 2' },
        ],
      },
    ],
  };

  it('debe inicializar el estado correctamente', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));
    expect(result.current.currentStep).toBe(0);
    expect(result.current.timeLeft).toBeGreaterThan(0);
    expect(result.current.choices).toEqual([]);
    expect(result.current.completed).toBe(false);
    expect(result.current.progress).toBe(0);
  });

  it('debe manejar nextStep correctamente', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));
    act(() => {
      result.current.nextStep();
    });
    expect(result.current.currentStep).toBe(1);
  });

  it('debe manejar prevStep correctamente', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));
    act(() => {
      result.current.nextStep();
      result.current.prevStep();
    });
    expect(result.current.currentStep).toBe(0);
  });

  it('debe manejar makeChoice correctamente', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));
    const mockOption: SceneOption = { id: 1, text: 'Opción 1' };
    act(() => {
      result.current.makeChoice(mockOption);
    });
    expect(result.current.choices).toContainEqual(mockOption);
  });

  it('debe manejar resetGame correctamente', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));
    act(() => {
      result.current.nextStep();
      result.current.resetGame();
    });
    expect(result.current.currentStep).toBe(0);
    expect(result.current.timeLeft).toBeGreaterThan(0);
    expect(result.current.choices).toEqual([]);
    expect(result.current.completed).toBe(false);
    expect(result.current.progress).toBe(0);
  });

  it('debe manejar completar el juego correctamente', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));
    mockScene.steps.forEach((step) => {
      const mockOption: SceneOption = step.options[0];
      act(() => {
        result.current.makeChoice(mockOption);
        result.current.nextStep();
      });
    });
    expect(result.current.completed).toBe(true);
  });

  it('debe manejar decisiones correctas e incorrectas', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));
    const mockOptionCorrect: SceneOption = { id: 1, text: 'Opción 1', isCorrect: true };
    const mockOptionIncorrect: SceneOption = { id: 2, text: 'Opción 2', isCorrect: false };
    act(() => {
      result.current.makeChoice(mockOptionCorrect);
      result.current.nextStep();
      result.current.makeChoice(mockOptionIncorrect);
      result.current.nextStep();
    });
    expect(result.current.choices).toContainEqual(mockOptionCorrect);
    expect(result.current.choices).toContainEqual(mockOptionIncorrect);
  });

  it('debe manejar tiempo correctamente', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    expect(result.current.timeLeft).toBeLessThan(mockScene.steps[0].timeLimit);
  });

  it('debe manejar decisiones con impactos en habilidades', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));
    const mockOption: SceneOption = { id: 1, text: 'Opción 1', skillImpacts: { 'Toma de decisiones': 10 } };
    act(() => {
      result.current.makeChoice(mockOption);
      result.current.nextStep();
    });
    expect(result.current.choices).toContainEqual(mockOption);
    expect(result.current.getSkillScores()).toHaveProperty('Toma de decisiones', 10);
  });
});