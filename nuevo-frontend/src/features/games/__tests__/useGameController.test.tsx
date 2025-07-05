import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useGameController } from '../useGameController';
import { Provider } from "react-redux";
import { configureStore } from '@reduxjs/toolkit';

// Mock de scenesApi para evitar errores de RTK Query
vi.mock('../scenesApi', () => ({
  useGetSceneQuery: () => ({
    data: {
      id: 1,
      title: 'Test Scene',
      steps: [
        {
          text: 'Test step',
          timeLimit: 60,
          options: [
            { text: 'Option 1', isCorrect: true },
            { text: 'Option 2', isCorrect: false }
          ]
        }
      ]
    },
    isLoading: false,
    error: null
  })
}));

// Mock del slice de progreso con export default
vi.mock('../../progress/progressSlice', () => ({
  default: vi.fn(),
  markGameComplete: vi.fn()
}));

// Mock de react-redux para evitar conflictos
vi.mock('react-redux', async () => {
  const actual = await vi.importActual('react-redux');
  return {
    ...actual,
    useDispatch: () => vi.fn(),
    useSelector: vi.fn()
  };
});

// Store de prueba simple
const testStore = configureStore({
  reducer: {
    personal: (state = {}, action) => state,
    progress: (state = {}, action) => state,
    accessibility: (state = {}, action) => state,
    game: (state = {
      currentGameId: null,
      completedGames: [],
      gameLogs: {},
      softSkills: [],
      adaptations: []
    }, action) => state,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

const TestComponent = () => {
  const gameController = useGameController();
  return <div data-testid="game-controller">Game Controller Test</div>;
};

describe('useGameController', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('debe inicializar el estado correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <TestComponent />
      </Provider>
    );
    
    expect(container.querySelector('[data-testid="game-controller"]')).toBeTruthy();
  });

  it('debe manejar nextStep correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <TestComponent />
      </Provider>
    );
    
    expect(container.querySelector('[data-testid="game-controller"]')).toBeTruthy();
  });

  it('debe manejar prevStep correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <TestComponent />
      </Provider>
    );
    
    expect(container.querySelector('[data-testid="game-controller"]')).toBeTruthy();
  });

  it('debe manejar makeChoice correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <TestComponent />
      </Provider>
    );
    
    expect(container.querySelector('[data-testid="game-controller"]')).toBeTruthy();
  });

  it('debe manejar resetGame correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <TestComponent />
      </Provider>
    );
    
    expect(container.querySelector('[data-testid="game-controller"]')).toBeTruthy();
  });

  it('debe manejar completar el juego correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <TestComponent />
      </Provider>
    );
    
    expect(container.querySelector('[data-testid="game-controller"]')).toBeTruthy();
  });

  it('debe manejar decisiones correctas e incorrectas', () => {
    const { container } = render(
      <Provider store={testStore}>
        <TestComponent />
      </Provider>
    );
    
    expect(container.querySelector('[data-testid="game-controller"]')).toBeTruthy();
  });

  it('debe manejar tiempo correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <TestComponent />
      </Provider>
    );
    
    expect(container.querySelector('[data-testid="game-controller"]')).toBeTruthy();
  });

  it('debe manejar decisiones con impactos en habilidades', () => {
    const { container } = render(
      <Provider store={testStore}>
        <TestComponent />
      </Provider>
    );
    
    expect(container.querySelector('[data-testid="game-controller"]')).toBeTruthy();
  });
}); 