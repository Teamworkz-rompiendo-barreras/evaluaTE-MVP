// src/pages/ResultadosPage.test.tsx

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom'; // Asegúrate de importar extend-expect para usar matchers de jest-dom
import ResultadosPage from './ResultadosPage';
import { MockedProvider } from '@apollo/client/testing';
import { GET_EVALUATION_RESULTS } from './queries'; // Asegúrate de que la consulta GraphQL esté correctamente importada
import { MemoryRouter } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from '@reduxjs/toolkit';
import { useGetSceneQuery } from "../features/games/scenesApi";

// Store de prueba simple
const testStore = configureStore({
  reducer: {
    personal: (state = {}, action) => state,
    progress: (state = {}, action) => state,
    accessibility: (state = {}, action) => state,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

// Mock de los datos de evaluación
const mockEvaluationResults = {
  request: {
    query: GET_EVALUATION_RESULTS,
    variables: { /* ... */ },
  },
  result: {
    data: {
      evaluationResults: {
        userId: 'uuid',
        softSkillsScores: {
          Resolucion_de_Problemas: 78,
          Gestion_emocional: 54,
          Trabajo_en_equipo: 85,
          Curiosidad_y_aprendizaje_continuo: 90,
          Resiliencia_y_flexibilidad: 80,
          Autoconciencia: 75,
          Empatia: 95,
          Escucha_activa: 88,
          Gestion_del_tiempo: 82,
        },
        employabilityScore: 78,
        level: 'Empleabilidad_media',
        cvScore: 62,
        adjustedScore: 78,
        nextSteps: [
          { id: 1, description: "Próximos pasos sugeridos" },
          { id: 2, description: "Formación sugerida" }
        ],
      },
    },
  },
};

describe('ResultadosPage', () => {
  it('muestra el título del informe correctamente', () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
            <ResultadosPage />
          </MockedProvider>
        </MemoryRouter>
      </Provider>
    );

    expect(container.textContent).toContain('Tu Informe Final');
  });

  it('muestra el mapa de habilidades correctamente', async () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
            <ResultadosPage />
          </MockedProvider>
        </MemoryRouter>
      </Provider>
    );

    // Espera a que los datos se carguen
    await screen.findByTestId('radar-chart');
    expect(container.querySelector('[data-testid="radar-chart"]')).toBeTruthy();
  });

  it('muestra las fortalezas más destacadas correctamente', async () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
            <ResultadosPage />
          </MockedProvider>
        </MemoryRouter>
      </Provider>
    );

    // Espera a que los datos se carguen
    await screen.findByText(/Fortalezas más destacadas/i);
    expect(container.textContent).toContain('Fortalezas más destacadas');
    expect(container.textContent).toContain('Resolución de Problemas: Alto');
    expect(container.textContent).toContain('Trabajo en equipo: Alto');
  });

  it('muestra las áreas de mejora correctamente', async () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
            <ResultadosPage />
          </MockedProvider>
        </MemoryRouter>
      </Provider>
    );

    // Espera a que los datos se carguen
    await screen.findByText(/Áreas a mejorar/i);
    expect(container.textContent).toContain('Áreas a mejorar');
    expect(container.textContent).toContain('Gestión emocional');
    expect(container.textContent).toContain('Curiosidad y aprendizaje continuo');
  });

  it('muestra las recomendaciones laborales correctamente', async () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
            <ResultadosPage />
          </MockedProvider>
        </MemoryRouter>
      </Provider>
    );

    // Espera a que los datos se carguen
    await screen.findByText(/Recomendaciones laborales/i);
    expect(container.textContent).toContain('Recomendaciones laborales');
    expect(container.textContent).toContain('Tipos de puestos recomendados');
    expect(container.textContent).toContain('Entornos preferibles');
  });

  it('muestra el análisis del CV correctamente', async () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
            <ResultadosPage />
          </MockedProvider>
        </MemoryRouter>
      </Provider>
    );

    // Espera a que los datos se carguen
    await screen.findByText(/Análisis de tu CV/i);
    expect(container.textContent).toContain('Análisis de tu CV');
    expect(container.textContent).toContain('CV bien estructurado');
    expect(container.textContent).toContain('Recomendación: añadir habilidades duras');
  });

  it('muestra los próximos pasos sugeridos correctamente', async () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
            <ResultadosPage />
          </MockedProvider>
        </MemoryRouter>
      </Provider>
    );

    // Espera a que los datos se carguen
    await screen.findByText(/Próximos pasos sugeridos/i);
    expect(container.textContent).toContain('Próximos pasos sugeridos');
    expect(container.textContent).toContain('Formación sugerida');
    expect(container.textContent).toContain('Portales de empleo recomendados');
  });

  it('muestra los botones de descarga y envío de correo correctamente', async () => {
    const { container } = render(
      <Provider store={testStore}>
        <MemoryRouter>
          <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
            <ResultadosPage />
          </MockedProvider>
        </MemoryRouter>
      </Provider>
    );

    // Espera a que los datos se carguen
    await screen.findByText(/Descargar Informe PDF/i);
    expect(container.textContent).toContain('Descargar Informe PDF');

    await screen.findByText(/Enviar por email/i);
    expect(container.textContent).toContain('Enviar por email');

    await screen.findByText(/Repetir evaluación/i);
    expect(container.textContent).toContain('Repetir evaluación');
  });
});