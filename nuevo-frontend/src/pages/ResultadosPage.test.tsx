// src/pages/ResultadosPage.test.tsx

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect'; // Asegúrate de importar extend-expect para usar matchers de jest-dom
import ResultadosPage from './ResultadosPage';
import { MockedProvider } from '@apollo/client/testing';
import { GET_EVALUATION_RESULTS } from './queries'; // Asegúrate de que la consulta GraphQL esté correctamente importada

// Mock de los datos de evaluación
const mockEvaluationResults = {
  request: {
    query: GET_EVALUATION_RESULTS,
  },
  result: {
    data: {
      evaluationResults: {
        userId: 'uuid',
        softSkillsScores: {
          Resolución_de_Problemas: 78,
          Gestión_emocional: 54,
          Trabajo_en_equipo: 85,
          Curiosidad_y_aprendizaje_continuo: 90,
          Resiliencia_y_flexibilidad: 80,
          Autoconciencia: 75,
          Empatía: 95,
          Escucha_activa: 88,
          Gestión_del_tiempo: 82,
        },
        employabilityScore: 78,
        level: 'Empleabilidad_media',
        cvScore: 62,
        adjustedScore: 78,
      },
    },
  },
};

describe('ResultadosPage', () => {
  it('muestra el título del informe correctamente', () => {
    render(
      <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
        <ResultadosPage />
      </MockedProvider>
    );

    expect(screen.getByText('Tu Informe Final')).toBeInTheDocument();
  });

  it('muestra el mapa de habilidades correctamente', async () => {
    render(
      <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
        <ResultadosPage />
      </MockedProvider>
    );

    // Espera a que los datos se carguen
    const radarChart = await screen.findByTestId('radar-chart');
    expect(radarChart).toBeInTheDocument();
  });

  it('muestra las fortalezas más destacadas correctamente', async () => {
    render(
      <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
        <ResultadosPage />
      </MockedProvider>
    );

    // Espera a que los datos se carguen
    const fortalezas = await screen.findByText(/Fortalezas más destacadas/i);
    expect(fortalezas).toBeInTheDocument();
    expect(screen.getByText(/Resolución de Problemas: Alto/i)).toBeInTheDocument();
    expect(screen.getByText(/Trabajo en equipo: Alto/i)).toBeInTheDocument();
  });

  it('muestra las áreas de mejora correctamente', async () => {
    render(
      <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
        <ResultadosPage />
      </MockedProvider>
    );

    // Espera a que los datos se carguen
    const areasDeMejora = await screen.findByText(/Áreas a mejorar/i);
    expect(areasDeMejora).toBeInTheDocument();
    expect(screen.getByText(/Gestión emocional/i)).toBeInTheDocument();
    expect(screen.getByText(/Curiosidad y aprendizaje continuo/i)).toBeInTheDocument();
  });

  it('muestra las recomendaciones laborales correctamente', async () => {
    render(
      <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
        <ResultadosPage />
      </MockedProvider>
    );

    // Espera a que los datos se carguen
    const recomendaciones = await screen.findByText(/Recomendaciones laborales/i);
    expect(recomendaciones).toBeInTheDocument();
    expect(screen.getByText(/Tipos de puestos recomendados/i)).toBeInTheDocument();
    expect(screen.getByText(/Entornos preferibles/i)).toBeInTheDocument();
  });

  it('muestra el análisis del CV correctamente', async () => {
    render(
      <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
        <ResultadosPage />
      </MockedProvider>
    );

    // Espera a que los datos se carguen
    const cvAnalysis = await screen.findByText(/Análisis de tu CV/i);
    expect(cvAnalysis).toBeInTheDocument();
    expect(screen.getByText(/CV bien estructurado/i)).toBeInTheDocument();
    expect(screen.getByText(/Recomendación: añadir habilidades duras/i)).toBeInTheDocument();
  });

  it('muestra los próximos pasos sugeridos correctamente', async () => {
    render(
      <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
        <ResultadosPage />
      </MockedProvider>
    );

    // Espera a que los datos se carguen
    const proximosPasos = await screen.findByText(/Próximos pasos sugeridos/i);
    expect(proximosPasos).toBeInTheDocument();
    expect(screen.getByText(/Formación sugerida/i)).toBeInTheDocument();
    expect(screen.getByText(/Portales de empleo recomendados/i)).toBeInTheDocument();
  });

  it('muestra los botones de descarga y envío de correo correctamente', async () => {
    render(
      <MockedProvider mocks={[mockEvaluationResults]} addTypename={false}>
        <ResultadosPage />
      </MockedProvider>
    );

    // Espera a que los datos se carguen
    const descargarInforme = await screen.findByText(/Descargar informe en PDF/i);
    expect(descargarInforme).toBeInTheDocument();

    const enviarCorreo = await screen.findByText(/Enviar por email/i);
    expect(enviarCorreo).toBeInTheDocument();

    const repetirEvaluacion = await screen.findByText(/Repetir evaluación/i);
    expect(repetirEvaluacion).toBeInTheDocument();
  });
});