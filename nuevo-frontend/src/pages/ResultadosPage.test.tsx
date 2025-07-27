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

// Configuración del servidor mock con msw
const server = setupServer(
  http.post('*/api/informe-ia', () => {
    return HttpResponse.json({
      summary: "Resumen del informe de empleabilidad",
      level: "Alta empleabilidad",
      employabilityScore: 85,
      recommendations: {
        roles: ["Desarrollador Frontend", "Project Manager Junior"],
        resources: ["Platzi", "Microsoft Learn"],
        cvImprovements: ["Mejorar la estructura", "Agregar más detalles"],
        nextSteps: ["Actualizar LinkedIn", "Completar cursos"]
      },
      report: {
        softSkills: [
          { skill: "Resolución de Problemas", score: 90, level: "Alto" },
          { skill: "Trabajo en equipo", score: 85, level: "Alto" },
          { skill: "Gestión emocional", score: 50, level: "Medio" }
        ],
        jobPreferences: {
          areas: ["Tecnología", "Desarrollo"],
          workMode: "remoto",
          availability: "completa"
        }
      },
      createdAt: new Date().toISOString()
    });
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
      // Comprobar elementos esenciales que siempre deben estar presentes
      expect(screen.getByText('Informe de Empleabilidad')).toBeInTheDocument();
      expect(screen.getByText('Mapa de habilidades')).toBeInTheDocument();
    });

    // Comprobar que el informe de IA se generó correctamente
    await waitFor(() => {
      expect(screen.getByText(/Resumen del informe de empleabilidad/)).toBeInTheDocument();
      expect(screen.getByText(/Project Manager Junior/)).toBeInTheDocument();
      expect(screen.getByText(/Desarrollador Frontend/)).toBeInTheDocument();
    });
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