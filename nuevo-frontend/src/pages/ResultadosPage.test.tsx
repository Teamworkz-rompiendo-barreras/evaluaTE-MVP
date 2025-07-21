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
    structure: 'CV bien estructurado',
    coherence: 'Buena coherencia',
    experience: 'Experiencia relevante',
    skills: ['JavaScript', 'React'],
    education: ['Universidad X'],
    alerts: ['Falta de habilidades duras', 'Necesita más proyectos'],
    feedback: 'CV bien estructurado y con información relevante.'
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

    expect(container.textContent).toContain('Informe de Empleabilidad');
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
    expect(container.textContent).toContain('Estructura: CV bien estructurado');
    expect(container.textContent).toContain('Habilidades Detectadas: JavaScript, React');
  });

  it('muestra el feedback general del CV', () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <ResultadosPage />
        </MemoryRouter>
      </Provider>
    );

    expect(container.textContent).toContain('Feedback General');
    expect(container.textContent).toContain('CV bien estructurado y con información relevante.');
  });

  it('muestra las habilidades blandas evaluadas correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <ResultadosPage />
        </MemoryRouter>
      </Provider>
    );

    expect(container.textContent).toContain('Mapa de habilidades');
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

    expect(container.textContent).toContain('Áreas de mejora y sugerencias');
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

    expect(container.textContent).toContain('Recomendaciones laborales');
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

    expect(container.textContent).toContain('Resumen de niveles:');
    expect(container.textContent).toContain('Puntaje global de empleabilidad');
    expect(container.textContent).toContain('78');
  });
});