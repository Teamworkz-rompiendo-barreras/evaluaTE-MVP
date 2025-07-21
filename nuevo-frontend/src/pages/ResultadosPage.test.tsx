/* eslint-env jest */
// src/pages/ResultadosPage.test.tsx

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from '@reduxjs/toolkit';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

import ResultadosPage from './ResultadosPage';
import { API_CONFIG, buildApiUrl } from '../config/api';

// Datos mock para el store de Redux
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
    userId: 'test-user-123',
    firstName: 'Juan',
    lastName: 'Candidato',
    jobPreferences: {
      areas: ['Tecnología', 'Consultoría']
    },
    softSkills: [
      {
        skill: 'Resolución de Problemas',
        level: 'Alto',
        confidence: 0.9,
        feedback: 'Excelente capacidad de resolución',
        score: 90,
        interactions: []
      },
      {
        skill: 'Trabajo en equipo',
        level: 'Alto',
        confidence: 0.85,
        feedback: 'Muy buen trabajo colaborativo',
        score: 85,
        interactions: []
      },
      {
        skill: 'Gestión emocional',
        level: 'Medio',
        confidence: 0.5,
        feedback: 'Necesitas mejorar el control emocional',
        score: 50,
        interactions: []
      }
    ],
    employabilityScore: 78,
    level: 'Empleabilidad_media',
    adjustedScore: 82,
    completedGames: ['game1', 'game2', 'game3', 'game4', 'game5', 'game6', 'game7', 'game8', 'game9', 'game10']
  }
};

// Informe mock que la IA debería generar
const mockIaReport = `
## Análisis de tu CV
Tu CV está bien estructurado.

## Tus Puntos Fuertes
- **Resolución de Problemas:** Demostrado en tu experiencia.

## Áreas de Desarrollo y Sugerencias Prácticas
- **Gestión Emocional:** Considera un curso de mindfulness.

## Recomendaciones Laborales
- Podrías encajar como **Project Manager Junior**.

## Próximos Pasos para tu Carrera
1.  Actualiza tu perfil de LinkedIn.
`;

// Configuración del servidor mock con msw
const server = setupServer(
  http.post(buildApiUrl(API_CONFIG.ENDPOINTS.IA_REPORT), () => {
    return HttpResponse.json({ informe: mockIaReport });
  })
);

// Store de prueba
const createTestStore = (initialState: any) => configureStore({
  reducer: {
    personal: (state = initialState.personal, action) => state,
    game: (state = initialState.game, action) => state,
    progress: (state = {}, action) => state,
    accessibility: (state = {}, action) => state,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({ serializableCheck: false }),
});

describe('ResultadosPage', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  it('muestra el informe generado por la IA correctamente', async () => {
    const store = createTestStore({
      personal: mockPersonalState,
      game: { completedGames: ['game1'] }
    });

    render(
      <Provider store={store}>
        <MemoryRouter>
          <ResultadosPage />
        </MemoryRouter>
      </Provider>
    );

    // Esperar a que el contenido de la IA se renderice
    await waitFor(() => {
      // Comprobar que los títulos del informe generado por la IA están presentes
      expect(screen.getByText('Análisis de tu CV')).toBeInTheDocument();
      expect(screen.getByText('Tus Puntos Fuertes')).toBeInTheDocument();
      expect(screen.getByText('Áreas de Desarrollo y Sugerencias Prácticas')).toBeInTheDocument();
      expect(screen.getByText('Recomendaciones Laborales')).toBeInTheDocument();
      expect(screen.getByText('Próximos Pasos para tu Carrera')).toBeInTheDocument();
    });

    // Comprobar contenido específico del informe
    expect(screen.getByText(/Tu CV está bien estructurado/)).toBeInTheDocument();
    expect(screen.getByText(/Project Manager Junior/)).toBeInTheDocument();
  });

  it('muestra el radar de habilidades y la portada', () => {
    const store = createTestStore({
      personal: mockPersonalState,
      game: { completedGames: [] } // No llamar a la IA en este test
    });

    render(
      <Provider store={store}>
        <MemoryRouter>
          <ResultadosPage />
        </MemoryRouter>
      </Provider>
    );

    expect(screen.getByText('Informe de Empleabilidad')).toBeInTheDocument();
    expect(screen.getByText('Mapa de habilidades')).toBeInTheDocument();
    expect(screen.getByText('Resumen de niveles:')).toBeInTheDocument();
  });
});