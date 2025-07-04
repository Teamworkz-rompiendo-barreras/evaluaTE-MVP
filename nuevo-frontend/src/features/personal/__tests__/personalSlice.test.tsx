// src/features/personal/__tests__/personalSlice.test.tsx
import { describe, it, expect } from 'vitest';
import { personalSlice } from '../personalSlice';

const initialState = personalSlice.getInitialState();

// Tipos compartidos desde el proyecto
import type {
  JobPreference,
  EmployabilityReport,
  AccessibilitySettings,
} from '../../../types/preferences';
import type { SoftSkillResult, GameDecisionLog } from '../../../types/skills';
import type { CvAnalysis } from '../../../types/preferences';

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
  structure: 'bueno',
  coherence: 'bueno',
  experience: 'regular',
  skills: ['Comunicación', 'Trabajo en equipo'],
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
    const mockFilePayload = { fileName: mockFile.name, fileContent: '' }; // Simulate empty content for test
    const action = personalSlice.actions.saveCV(mockFilePayload);

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      cvFile: mockFilePayload,
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
  });