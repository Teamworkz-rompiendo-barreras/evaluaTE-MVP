// src/features/personal/personalSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { CvAnalysis, JobPreference, AccessibilitySettings, EmployabilityReport, SoftSkillResult } from '@/types/preferences';
import type { UserDecision } from '../../types/skills'; // Adjust the import path as needed

// Define SceneLog type if not imported from elsewhere
export interface SceneLog {
  sceneId: string;
  decisions: UserDecision[];
  totalSteps: number;
  totalTime: number;
  averageConfidence: number;
  emotionalTrend: string[];
  accessibilityUsed: boolean;
  accessibilitySettings?: AccessibilitySettings;
}

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
  logs: SceneLog[];

  accessibilitySettings?: AccessibilitySettings;
  
  // Campo para marcar si los datos personales están completos
  completed: boolean;
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
  
  // Inicialmente los datos personales no están completos
  completed: false,
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
      // Solo actualiza los campos del payload, no borra el resto del estado
      state.firstName = action.payload.firstName;
      state.lastName = action.payload.lastName;
      state.email = action.payload.email;
      state.whatsapp = action.payload.whatsapp;
      state.unlockedGames = Math.max(state.unlockedGames, 1);
      // Marcamos como completado cuando se guardan los datos de contacto
      // (aunque técnicamente no están completamente completos hasta las preferencias)
      state.completed = true;
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
      // Eliminar o comentar los console.log
      // Cambiar 'any' por 'unknown' o un tipo más específico
      
      const payload = action.payload;

      // Actualizar directamente los campos del estado
      state.jobPreferences = payload.jobPreferences;
      state.workMode = payload.workMode;
      state.availability = payload.availability;
      state.startDate = payload.startDate;
      state.willingToRelocate = payload.willingToRelocate;
      state.hasDisabilityCert = payload.hasDisabilityCert;
      
      // Asegurar que completed esté en true
      state.completed = true;
      
      // Eliminar o comentar los console.log
      // Cambiar 'any' por 'unknown' o un tipo más específico
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
      const logs = (state.report && Array.isArray(state.report as unknown))
        ? (state.report as unknown as SceneLog[])
        : [];

      const existingIndex: number = logs.findIndex((log: SceneLog) => log.sceneId === String(sceneId));

      if (existingIndex > -1) {
        logs[existingIndex].decisions.push(action.payload);
        state.report = {
          ...((state.report ?? {}) as EmployabilityReport),
        } as EmployabilityReport;
      } else {
        state.logs = [
          ...logs,
          {
            sceneId: String(sceneId),
            decisions: [action.payload],
            totalSteps: 5,
            totalTime: 300,
            averageConfidence: action.payload.skillImpacts[action.payload.optionText] || 0.6,
            emotionalTrend: ['positivo', 'neutro'] as ('positivo' | 'neutro' | 'negativo')[],
            accessibilityUsed: !!state.accessibilitySettings,
            accessibilitySettings: state.accessibilitySettings,
          },
        ];
      }
    },

    // Guarda configuración de accesibilidad
    setAccessibilitySettings(state, action: PayloadAction<AccessibilitySettings>) {
      state.accessibilitySettings = action.payload;
    },

    // Marca los datos personales como completos
    setPersonalCompleted(state, action: PayloadAction<boolean>) {
      state.completed = action.payload;
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
      if (
        state.cvAnalysis &&
        typeof (state.cvAnalysis as unknown) === 'number' &&
        (state.cvAnalysis as unknown) < 60
      ) {
        employabilityScore = Math.max(20, employabilityScore - 10);
      }

      // Nivel de empleabilidad
      const level: 'bajo' | 'medio' | 'alto' =
        employabilityScore >= 80
          ? 'alto'
          : employabilityScore >= 50
          ? 'medio'
          : 'bajo';

      // Recomendaciones personalizadas
      const recommendationsObj = getRecommendationsFromProfile({
        softSkills: state.softSkills,
        cvAnalysis: state.cvAnalysis,
        preferences: state.jobPreferences as JobPreference,
        hasDisabilityCert: state.hasDisabilityCert,
      });
      // Flatten recommendations object into a string array
      const recommendations: string[] = [
        ...recommendationsObj.roles.map(role => `Rol recomendado: ${role}`),
        ...recommendationsObj.resources.map(resource => `Recurso sugerido: ${resource}`),
        ...recommendationsObj.cvImprovements.map(improvement => `Mejora de CV: ${improvement}`),
        ...recommendationsObj.nextSteps.map(step => `Próximo paso: ${step}`),
      ];

      // Actualiza el estado del informe
      state.report = {
        userId: 'user-ester-2025',
        firstName: state.firstName,
        lastName: state.lastName,
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
        adjustedScore: employabilityScore,
      } as EmployabilityReport;
    },

    // Reinicia todo el estado
    resetPersonalState() {
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
  if (params.softSkills.some(skill => skill.level === 'alto')) {
    roles.push('Desarrollador frontend');
    roles.push('Soporte técnico');
    resources.push('Platzi');
    resources.push('Microsoft Learn');
  }

  if (params.cvAnalysis && Array.isArray(params.cvAnalysis) && params.cvAnalysis.length) {
    cvImprovements.push(...params.cvAnalysis);
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
  setPersonalCompleted,
} = personalSlice.actions;

// Exportamos el reducer
export default personalSlice.reducer;