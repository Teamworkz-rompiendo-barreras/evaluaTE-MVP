// src/features/personal/personalSlice.ts
import { createSlice, PayloadAction, Draft } from '@reduxjs/toolkit';
import type { CvAnalysis, JobPreference, AccessibilitySettings, EmployabilityReport, SoftSkillResult } from '@/types/preferences';
import type { GameDecisionLog } from '../../types/game'; // Adjust the import path as needed

export interface PersonalState {
  firstName: string;
  lastName: string;
  email: string;
  whatsapp: string;

  jobPreferences: string | JobPreference;
  workMode?: 'remoto' | 'presencial' | 'híbrido';
  availability?: 'mañana' | 'tarde' | 'completa';
  startDate?: 'inmediata' | '15_días' | '1_mes' | 'más_de_1_mes';
  willingToRelocate: boolean;
  hasDisabilityCert: boolean;

  cvFile: { fileName: string; fileContent: string } | null;
  cvAnalysis?: CvAnalysis;

  softSkills: SoftSkillResult[];
  unlockedGames: number;

  report?: EmployabilityReport;
  logs: GameDecisionLog[];

  accessibilitySettings?: AccessibilitySettings;
}

// Estado inicial
const initialState: PersonalState = {
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
};

// Definición del slice
export const personalSlice = createSlice({
  name: 'personal',
  initialState,
  reducers: {
    // Guarda datos personales
    saveContact(
      state,
      action: PayloadAction<
        Pick<PersonalState, 'firstName' | 'lastName' | 'email' | 'whatsapp'>
      >
    ) {
      return {
        ...state,
        ...action.payload,
        unlockedGames: Math.max(state.unlockedGames, 1),
      };
    },

    // Guarda preferencias laborales
    savePreferences(
      state,
      action: PayloadAction<
        Pick<
          PersonalState,
          'jobPreferences' | 'workMode' | 'availability' | 'startDate' | 'willingToRelocate' | 'hasDisabilityCert'
        >
      >
    ) {
      const payload = action.payload;

      if (typeof payload.jobPreferences === 'string') {
        payload.jobPreferences = {
          areas: [payload.jobPreferences],
          needs: [],
          workMode: payload.workMode || 'remoto',
          availability: payload.availability || 'completa',
          willingToRelocate: payload.willingToRelocate,
          hasDisabilityCert: payload.hasDisabilityCert,
          accessibilitySettings: state.accessibilitySettings,
        };
      }

      return {
        ...state,
        ...payload,
        unlockedGames: Math.min(10, state.unlockedGames + 1),
      };
    },

    // Guarda archivo del CV
    saveCV(state, action: PayloadAction<{ fileName: string; fileContent: string }>) {
      return {
        ...state,
        cvFile: action.payload,
        unlockedGames: Math.min(10, state.unlockedGames + 1),
      };
    },

    // Guarda análisis del CV
    saveCvAnalysis(state, action: PayloadAction<CvAnalysis>) {
      return {
        ...state,
        cvAnalysis: action.payload,
        unlockedGames: Math.min(10, state.unlockedGames + 1),
      };
    },

    // Desbloquea siguiente minijuego
    unlockNextGame(state) {
      if (state.unlockedGames < 10) {
        state.unlockedGames += 1;
      }
    },

    // Guarda habilidades blandas evaluadas
    saveSoftSkills(state, action: PayloadAction<SoftSkillResult[]>) {
      return {
        ...state,
        softSkills: [...state.softSkills, ...action.payload],
      };
    },

    // Registra decisiones tomadas durante escenas
    addSceneDecision(state, action: PayloadAction<UserDecision>) {
      const sceneId = action.payload.sceneId;
      const existingIndex = state.report?.logs.findIndex(log => log.sceneId === sceneId);

      if (existingIndex !== undefined && existingIndex > -1) {
        state.report!.logs[existingIndex].decisions.push(action.payload);
      } else {
        state.report = {
          ...state.report!,
          logs: [
            ...(state.report?.logs || []),
            {
              sceneId,
              decisions: [action.payload],
              totalSteps: 5,
              totalTime: 300,
              averageConfidence: action.payload.skillImpacts[action.payload.optionText] || 0.6,
              emotionalTrend: ['positivo', 'neutro'],
              accessibilityUsed: !!state.accessibilitySettings,
              accessibilitySettings: state.accessibilitySettings,
            },
          ],
        };
      }
    },

    // Guarda configuración de accesibilidad
    setAccessibilitySettings(state, action: PayloadAction<AccessibilitySettings>) {
      state.accessibilitySettings = action.payload;
    },

    // Genera informe final basado en todo el progreso
    generateFinalReport(state) {
      const totalSoftSkills = state.softSkills.length;
      const highSkills = state.softSkills.filter(skill => skill.level === 'alto').length;
      const mediumSkills = state.softSkills.filter(skill => skill.level === 'medio').length;
      const lowSkills = state.softSkills.filter(skill => skill.level === 'bajo').length;

      let employabilityScore = 0;
      if (totalSoftSkills > 0) {
        employabilityScore = Math.round(
          ((highSkills * 100 + mediumSkills * 70 + lowSkills * 30) / totalSoftSkills)
        );
      }

      // Ajuste según el CV
      if (state.cvAnalysis?.score && state.cvAnalysis.score < 60) {
        employabilityScore = Math.max(20, employabilityScore - 10);
      }

      // Nivel de empleabilidad
      const level: 'Baja empleabilidad' | 'Empleabilidad media' | 'Alta empleabilidad' =
        employabilityScore >= 80
          ? 'Alta empleabilidad'
          : employabilityScore >= 50
          ? 'Empleabilidad media'
          : 'Baja empleabilidad';

      // Recomendaciones personalizadas
      const recommendations = getRecommendationsFromProfile({
        softSkills: state.softSkills,
        cvAnalysis: state.cvAnalysis,
        preferences: state.jobPreferences as JobPreference,
        hasDisabilityCert: state.hasDisabilityCert,
      });

      // Actualiza el estado del informe
      state.report = {
        userId: 'user-ester-2025',
        fullName: `${state.firstName} ${state.lastName}`,
        softSkills: state.softSkills,
        employabilityScore,
        jobPreferences:
          typeof state.jobPreferences === 'string'
            ? {
                areas: [state.jobPreferences],
                needs: [],
                workMode: state.workMode,
                availability: state.availability,
                willingToRelocate: state.willingToRelocate,
                hasDisabilityCert: state.hasDisabilityCert,
                accessibilitySettings: state.accessibilitySettings,
              }
            : {
                ...state.jobPreferences,
                willingToRelocate: state.willingToRelocate,
                hasDisabilityCert: state.hasDisabilityCert,
              },
        cvAnalysis: state.cvAnalysis,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        completedGames: Array.from({ length: state.unlockedGames }, (_, i) => i + 1),
        level,
        recommendations,
        logs: state.logs,
      };
    },

    // Reinicia todo el estado
    resetPersonalState(state) {
      return initialState;
    },
  },
});

// Función auxiliar para generar recomendaciones
function getRecommendationsFromProfile(params: {
  softSkills: SoftSkillResult[];
  cvAnalysis?: CvAnalysis;
  preferences: JobPreference;
  hasDisabilityCert: boolean;
}) {
  const roles: string[] = [];
  const resources: string[] = [];
  const cvImprovements: string[] = [];
  const nextSteps: string[] = [];

  // Ejemplo de lógica básica – puedes expandir esto desde backend o IA
  if (params.softSkills.some(skill => skill.level === 'Alto')) {
    roles.push('Desarrollador frontend');
    roles.push('Soporte técnico');
    resources.push('Platzi');
    resources.push('Microsoft Learn');
  }

  if (params.cvAnalysis?.weaknesses.length) {
    cvImprovements.push(...params.cvAnalysis.weaknesses);
  }

  nextSteps.push('Completar todos los juegos', 'Actualizar tu CV', 'Revisar tus preferencias');

  return {
    roles,
    resources,
    cvImprovements,
    nextSteps,
  };
}

// Exportamos las acciones
export const {
  saveContact,
  savePreferences,
  saveCV,
  saveCvAnalysis,
  unlockNextGame,
  saveSoftSkills,
  setAccessibilitySettings,
  addSceneDecision,
  generateFinalReport,
  resetPersonalState,
} = personalSlice.actions;

// Exportamos el reducer
export default personalSlice.reducer;