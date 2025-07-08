/* eslint-env jest */
// src/pages/ResultadosPage.test.tsx

import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResultadosPage from './ResultadosPage';
import { MemoryRouter } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from '@reduxjs/toolkit';

// Store de prueba con datos mockeados que coinciden con el componente real
const mockPersonalState = {
  cvAnalysis: {
    score: 85,
    strengths: ['CV bien estructurado', 'Experiencia relevante'],
    weaknesses: ['Falta de habilidades duras', 'Necesita más proyectos']
  },
  report: {
    softSkills: [
      {
        skill: 'Resolución de Problemas',
        level: 'Alto',
        confidence: 0.9,
        feedback: 'Excelente capacidad de resolución',
        interactions: []
      },
      {
        skill: 'Trabajo en equipo',
        level: 'Alto',
        confidence: 0.85,
        feedback: 'Muy buen trabajo colaborativo',
        interactions: []
      },
      {
        skill: 'Gestión emocional',
        level: 'Medio',
        confidence: 0.5,
        feedback: 'Necesitas mejorar el control emocional',
        interactions: []
      }
    ],
    employabilityScore: 78,
    level: 'Empleabilidad_media',
    adjustedScore: 82,
    completedGames: ['game1', 'game2', 'game3', 'game4', 'game5', 'game6', 'game7', 'game8', 'game9', 'game10']
  }
};

const testStore = configureStore({
  reducer: {
    personal: (state = mockPersonalState, action) => state,
    progress: (state = {}, action) => state,
    accessibility: (state = {}, action) => state,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

describe('ResultadosPage', () => {
  it('muestra el título del informe correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <ResultadosPage />
        </MemoryRouter>
      </Provider>
    );

    expect(container.textContent).toContain('Tu Informe Final');
  });

  it('muestra el análisis del CV correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <ResultadosPage />
        </MemoryRouter>
      </Provider>
    );

    expect(container.textContent).toContain('Análisis de tu CV');
    expect(container.textContent).toContain('CV bien estructurado');
    expect(container.textContent).toContain('Falta de habilidades duras');
  });

  it('muestra las habilidades blandas evaluadas correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <ResultadosPage />
        </MemoryRouter>
      </Provider>
    );

    expect(container.textContent).toContain('Habilidades Blandas Evaluadas');
    expect(container.textContent).toContain('Resolución de Problemas');
    expect(container.textContent).toContain('Trabajo en equipo');
  });

  it('muestra las fortalezas más destacadas correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <ResultadosPage />
        </MemoryRouter>
      </Provider>
    );

    expect(container.textContent).toContain('Fortalezas más destacadas');
    expect(container.textContent).toContain('Resolución de Problemas');
    expect(container.textContent).toContain('Trabajo en equipo');
  });

  it('muestra las áreas a mejorar correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <ResultadosPage />
        </MemoryRouter>
      </Provider>
    );

    expect(container.textContent).toContain('Áreas a mejorar');
    expect(container.textContent).toContain('Gestión emocional');
  });

  it('muestra las recomendaciones de mejora correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <ResultadosPage />
        </MemoryRouter>
      </Provider>
    );

    expect(container.textContent).toContain('Recomendaciones de mejora');
    expect(container.textContent).toContain('Gestión emocional');
  });

  it('muestra el resumen de habilidades correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <ResultadosPage />
        </MemoryRouter>
      </Provider>
    );

    expect(container.textContent).toContain('Resumen de habilidades');
    expect(container.textContent).toContain('Puntaje global de empleabilidad');
    expect(container.textContent).toContain('78');
  });

  it('muestra el botón de descarga correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <ResultadosPage />
        </MemoryRouter>
      </Provider>
    );

    expect(container.textContent).toContain('Descargar Informe PDF');
  });
});