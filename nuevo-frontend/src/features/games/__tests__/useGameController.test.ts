// nuevo-frontend/src/features/games/__tests__/useGameController.test.ts

import { renderHook, act } from '@testing-library/react-hooks';
import { useGameController } from '../useGameController';
import { GameScene, SceneOption } from '@/types/game-scene';
import { UserDecision } from '@/types/skills';

// Mock de la función getScene para simular la obtención de escenas
jest.mock('@/features/games/scenesApi', () => ({
  getScene: (sceneId: number) => (state: any) => state.scenes.find((scene: GameScene) => scene.sceneId === sceneId),
}));

// Estado inicial mockeado para las escenas
const mockScenes: GameScene[] = [
  {
    id: 1,
    sceneId: 1,
    title: 'Minijuego 1',
    description: 'Descripción del minijuego 1',
    steps: [
      {
        id: 1,
        description: 'Paso 1',
        options: [
          { id: 1, text: 'Opción 1', isCorrect: true, skillImpact: { 'Toma de decisiones': 10 } },
          { id: 2, text: 'Opción 2', isCorrect: false, skillImpact: { 'Toma de decisiones': 5 } },
        ],
        timeLimit: 30,
      },
    ],
    softSkillsTracked: ['Toma de decisiones'],
    accessibilityOptions: {
      showPictograms: true,
      audioAssistiveMode: true,
      contrastLevel: 'normal',
    },
  },
];

// Estado mockeado para el store
const mockState = {
  scenes: mockScenes,
};

// Mock del store
jest.mock('react-redux', () => ({
  ...jest.requireActual('react-redux'),
  useSelector: (selector: any) => selector(mockState),
}));

describe('useGameController', () => {
  const mockScene: GameScene = {
    id: 1,
    sceneId: 1,
    title: 'Minijuego 1',
    description: 'Descripción del minijuego 1',
    steps: [
      {
        id: 1,
        description: 'Paso 1',
        options: [
          { id: 1, text: 'Opción 1', isCorrect: true, skillImpact: { 'Toma de decisiones': 10 } },
          { id: 2, text: 'Opción 2', isCorrect: false, skillImpact: { 'Toma de decisiones': 5 } },
        ],
        timeLimit: 30,
      },
    ],
    softSkillsTracked: ['Toma de decisiones'],
    accessibilityOptions: {
      showPictograms: true,
      audioAssistiveMode: true,
      contrastLevel: 'normal',
    },
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
    const mockOption: SceneOption = { id: 1, text: 'Opción 1', isCorrect: true, skillImpact: { 'Toma de decisiones': 10 } };
    act(() => {
      result.current.makeChoice(mockOption);
    });
    expect(result.current.choices).toContainEqual({
      sceneId: mockScene.sceneId,
      stepIndex: 0,
      optionText: mockOption.text,
      isCorrect: mockOption.isCorrect,
      skillImpacts: mockOption.skillImpact,
      timestamp: expect.any(String),
      userAgent: expect.any(String),
      screenResolution: expect.any(String),
    });
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
    expect(result.current.progress).toBe(100);
  });

  it('debe manejar decisiones correctas e incorrectas', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));
    const mockOptionCorrect: SceneOption = { id: 1, text: 'Opción 1', isCorrect: true, skillImpact: { 'Toma de decisiones': 10 } };
    const mockOptionIncorrect: SceneOption = { id: 2, text: 'Opción 2', isCorrect: false, skillImpact: { 'Toma de decisiones': 5 } };
    act(() => {
      result.current.makeChoice(mockOptionCorrect);
      result.current.nextStep();
      result.current.makeChoice(mockOptionIncorrect);
      result.current.nextStep();
    });
    expect(result.current.choices).toContainEqual({
      sceneId: mockScene.sceneId,
      stepIndex: 0,
      optionText: mockOptionCorrect.text,
      isCorrect: mockOptionCorrect.isCorrect,
      skillImpacts: mockOptionCorrect.skillImpact,
      timestamp: expect.any(String),
      userAgent: expect.any(String),
      screenResolution: expect.any(String),
    });
    expect(result.current.choices).toContainEqual({
      sceneId: mockScene.sceneId,
      stepIndex: 1,
      optionText: mockOptionIncorrect.text,
      isCorrect: mockOptionIncorrect.isCorrect,
      skillImpacts: mockOptionIncorrect.skillImpact,
      timestamp: expect.any(String),
      userAgent: expect.any(String),
      screenResolution: expect.any(String),
    });
  });

  it('debe manejar tiempo correctamente', () => {
    jest.useFakeTimers(); // Utilizar temporizadores falsos para controlar el tiempo
    const { result } = renderHook(() => useGameController(mockScene.sceneId));
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    expect(result.current.timeLeft).toBe(29); // Asumiendo que timeLimit es 30
    jest.useRealTimers(); // Restaurar temporizadores reales
  });

  it('debe manejar decisiones con impactos en habilidades', () => {
    const { result } = renderHook(() => useGameController(mockScene.sceneId));
    const mockOption: SceneOption = { id: 1, text: 'Opción 1', isCorrect: true, skillImpact: { 'Toma de decisiones': 10 } };
    act(() => {
      result.current.makeChoice(mockOption);
      result.current.nextStep();
    });
    expect(result.current.choices).toContainEqual({
      sceneId: mockScene.sceneId,
      stepIndex: 0,
      optionText: mockOption.text,
      isCorrect: mockOption.isCorrect,
      skillImpacts: mockOption.skillImpact,
      timestamp: expect.any(String),
      userAgent: expect.any(String),
      screenResolution: expect.any(String),
    });
    expect(result.current.getSkillScores()).toHaveProperty('Toma de decisiones', 10);
  });
});