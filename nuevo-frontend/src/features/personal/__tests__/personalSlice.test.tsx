// src/features/personal/__tests__/personalSlice.test.tsx
import { describe, it, expect } from 'vitest';
import { personalSlice } from '../personalSlice';

// Tipos compartidos desde el proyecto
import type {
  JobPreference,
  EmployabilityReport,
  AccessibilitySettings,
} from '@/types/preferences';
import type { CvAnalysis, SoftSkillResult, GameDecisionLog } from '@/types/skills';

// Mock de los tipos necesarios
const mockJobPreference: JobPreference = {
  areas: ['Logística', 'Atención al cliente'],
  needs: ['Trabajo en entorno tranquilo'],
  workMode: 'presencial',
  availability: 'completa',
  willingToRelocate: false,
  hasDisabilityCert: false,
  accessibilitySettings: {
    easyReadingMode: true,
    audioAssistiveMode: false,
    showPictograms: true,
    contrastLevel: 'normal',
    fontScale: 120,
  },
};

const mockCvAnalysis: CvAnalysis = {
  score: 85,
  strengths: ['Toma de decisiones', 'Resolución de problemas'],
  weaknesses: ['Creatividad'],
  feedback: 'Buen trabajo general.',
  rawLog: {},
};

const mockSoftSkillResults: SoftSkillResult[] = [
  { skill: 'Toma de decisiones', level: 'Alto', confidence: 0.9, feedback: 'Excelente', interactions: [] },
  { skill: 'Resolución de problemas', level: 'Medio', confidence: 0.6, feedback: 'Bueno', interactions: [] },
  { skill: 'Creatividad', level: 'Bajo', confidence: 0.3, feedback: 'Necesitas mejorar', interactions: [] },
];

const mockGameDecisionLog: GameDecisionLog = {
  sceneId: 1,
  decisions: [
    {
      sceneId: 1,
      stepIndex: 0,
      optionText: 'Opción 1',
      isCorrect: true,
      skillImpacts: { 'Toma de decisiones': 10 },
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      screenResolution: `${window.innerWidth}x${window.innerHeight}`,
    },
  ],
  totalSteps: 5,
  totalTime: 300,
  averageConfidence: 0.9,
  emotionalTrend: ['positivo', 'neutro'],
  accessibilityUsed: true,
  accessibilitySettings: {
    easyReadingMode: true,
    audioAssistiveMode: false,
    showPictograms: true,
    contrastLevel: 'normal',
    fontScale: 120,
  },
};

describe('personalSlice', () => {
  it('debe inicializar con valores predeterminados', () => {
    const initialState = personalSlice.getInitialState();
    expect(initialState).toEqual({
      firstName: '',
      lastName: '',
      email: '',
      whatsapp: '',
      jobPreferences: '',
      workMode: 'remoto',
      availability: 'completa',
      startDate: 'inmediata',
      willingToRelocate: false,
      hasDisabilityCert: false,
      cvFile: null,
      cvAnalysis: undefined,
      softSkills: [],
      unlockedGames: 1,
      report: undefined,
      logs: [],
      accessibilitySettings: {
        easyReadingMode: false,
        audioAssistiveMode: false,
        showPictograms: false,
        contrastLevel: 'normal',
        fontScale: 120,
      },
    });
  });

  it('debe guardar datos personales correctamente', () => {
    const state = personalSlice.getInitialState();
    const action = personalSlice.actions.saveContact({
      firstName: 'Juan',
      lastName: 'Pérez',
      email: 'juan@example.com',
      whatsapp: '123456789',
    });

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      firstName: 'Juan',
      lastName: 'Pérez',
      email: 'juan@example.com',
      whatsapp: '123456789',
      unlockedGames: 1,
    });
  });

  it('debe guardar preferencias laborales correctamente', () => {
    const state = personalSlice.getInitialState();
    const action = personalSlice.actions.savePreferences({
      jobPreferences: mockJobPreference,
      workMode: 'presencial',
      availability: 'completa',
      startDate: 'inmediata',
      willingToRelocate: false,
      hasDisabilityCert: false,
    });

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      jobPreferences: mockJobPreference,
      workMode: 'presencial',
      availability: 'completa',
      startDate: 'inmediata',
      willingToRelocate: false,
      hasDisabilityCert: false,
      unlockedGames: 2,
    });
  });

  it('debe guardar archivo del CV correctamente', () => {
    const state = personalSlice.getInitialState();
    const mockFile = new File([''], 'example.pdf', { type: 'application/pdf' });
    const action = personalSlice.actions.saveCV(mockFile);

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      cvFile: mockFile,
      unlockedGames: 2,
    });
  });

  it('debe guardar análisis del CV correctamente', () => {
    const state = personalSlice.getInitialState();
    const action = personalSlice.actions.saveCvAnalysis(mockCvAnalysis);

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      cvAnalysis: mockCvAnalysis,
      unlockedGames: 2,
    });
  });

  it('debe desbloquear el siguiente minijuego correctamente', () => {
    const state = personalSlice.getInitialState();
    const action = personalSlice.actions.unlockNextGame();

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      unlockedGames: 2,
    });
  });

  it('debe guardar habilidades blandas evaluadas correctamente', () => {
    const state = personalSlice.getInitialState();
    const action = personalSlice.actions.saveSoftSkills(mockSoftSkillResults);

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      softSkills: mockSoftSkillResults,
    });
  });

  it('debe registrar decisiones tomadas durante escenas correctamente', () => {
    const state = personalSlice.getInitialState();
    const action = personalSlice.actions.addSceneDecision({
      sceneId: 1,
      stepIndex: 0,
      optionText: 'Opción 1',
      isCorrect: true,
      skillImpacts: { 'Toma de decisiones': 10 },
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      screenResolution: `${window.innerWidth}x${window.innerHeight}`,
    });

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      logs: [mockGameDecisionLog],
    });
  });

  it('debe guardar configuración de accesibilidad correctamente', () => {
    const state = personalSlice.getInitialState();
    const action = personalSlice.actions.setAccessibilitySettings({
      easyReadingMode: true,
      audioAssistiveMode: false,
      showPictograms: true,
      contrastLevel: 'normal',
      fontScale: 120,
    });

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      accessibilitySettings: {
        easyReadingMode: true,
        audioAssistiveMode: false,
        showPictograms: true,
        contrastLevel: 'normal',
        fontScale: 120,
      },
    });
  });

  it('debe generar informe final basado en todo el progreso correctamente', () => {
    const state = {
      ...personalSlice.getInitialState(),
      firstName: 'Juan',
      lastName: 'Pérez',
      email: 'juan@example.com',
      whatsapp: '123456789',
      jobPreferences: mockJobPreference,
      cvAnalysis: mockCvAnalysis,
      softSkills: mockSoftSkillResults,
      unlockedGames: 10,
      logs: [mockGameDecisionLog],
    };

    const action = personalSlice.actions.generateFinalReport();

    const newState = personalSlice.reducer(state, action);
    const employabilityScore = 67; // Calculado como (100 + 70 + 30) / 3 = 66.67 -> redondeado a 67
    const level = 'Empleabilidad media';
    const recommendations = {
      roles: ['Desarrollador frontend', 'Soporte técnico'],
      resources: ['Platzi', 'Microsoft Learn'],
      cvImprovements: ['Creatividad'],
      nextSteps: ['Completar todos los juegos', 'Actualizar tu CV', 'Revisar tus preferencias'],
    };

    expect(newState).toEqual({
      ...state,
      report: {
        userId: 'user-ester-2025',
        fullName: 'Juan Pérez',
        softSkills: mockSoftSkillResults,
        employabilityScore,
        jobPreferences: mockJobPreference,
        cvAnalysis: mockCvAnalysis,
        createdAt: expect.any(String),
        updatedAt: expect.any(String),
        completedGames: Array.from({ length: 10 }, (_, i) => i + 1),
        level,
        recommendations,
        logs: [mockGameDecisionLog],
      },
    });
  });

  it('debe reiniciar todo el estado correctamente', () => {
    const state = {
      ...personalSlice.getInitialState(),
      firstName: 'Juan',
      lastName: 'Pérez',
      email: 'juan@example.com',
      whatsapp: '123456789',
      jobPreferences: mockJobPreference,
      cvAnalysis: mockCvAnalysis,
      softSkills: mockSoftSkillResults,
      unlockedGames: 10,
      logs: [mockGameDecisionLog],
    };

    const action = personalSlice.actions.resetPersonalState();

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual(personalSlice.getInitialState());
  });
});