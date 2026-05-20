/* eslint-disable no-console */
// src/features/personal/personalSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { JobPreference, AccessibilitySettings, EmployabilityReport, SoftSkillResult } from '@/types/preferences';
import type { CvAnalysis } from '@/types/report';
import type { UserDecision } from '../../types/skills'; // Adjust the import path as needed
import { filterValidSoftSkills } from '../../utils/data-validation';

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
  /**
   * Resultado estructurado del análisis de CV.
   * Se tipa explícitamente con `CvAnalysis` para garantizar
   * que todos los campos esperados (structure_score, evidence,
   * corrections, etc.) estén presentes al almacenarlo.
   */
  cvAnalysis: CvAnalysis | undefined;

  softSkills: SoftSkillResult[];
  unlockedGames: number;

  report?: EmployabilityReport;
  logs: SceneLog[];

  accessibilitySettings?: AccessibilitySettings;

  // Campo para marcar si los datos personales están completos
  completed: boolean;
}

// Estado inicial del slice
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

// DEBUG: Log del estado inicial
if (import.meta?.env?.DEV) {
  console.log('🔍 DEBUG - Estado inicial del personalSlice:', initialState);
}


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
      state.firstName = action.payload.firstName;
      state.lastName = action.payload.lastName;
      state.email = action.payload.email;
      state.whatsapp = action.payload.whatsapp;
      state.unlockedGames = Math.max(state.unlockedGames, 1);
      // Solo marcamos como completado si también hay preferencias laborales
      state.completed = Boolean(
        state.firstName && state.lastName &&
        state.jobPreferences &&
        (typeof state.jobPreferences === 'string'
          ? state.jobPreferences.trim() !== ''
          : state.jobPreferences.areas && state.jobPreferences.areas.length > 0)
      );
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
      // Solo actualiza los campos de preferencias, nunca borra los de contacto
      state.jobPreferences = payload.jobPreferences;
      state.workMode = payload.workMode;
      state.availability = payload.availability;
      state.startDate = payload.startDate;
      state.willingToRelocate = payload.willingToRelocate;
      state.hasDisabilityCert = payload.hasDisabilityCert;
      // completed solo si hay datos de contacto Y preferencias (más robusto)
      state.completed = Boolean(
        state.firstName && state.lastName &&
        (
          typeof state.jobPreferences === 'string'
            ? state.jobPreferences.trim() !== ''
            : Array.isArray(state.jobPreferences.areas) && state.jobPreferences.areas.length > 0 && (state.jobPreferences.areas[0]?.trim() || '') !== ''
        )
      );
    },

    // Guarda archivo del CV
    saveCV(state, action: PayloadAction<{ fileName: string; fileContent: string }>) {
      return {
        ...state,
        cvFile: action.payload,
        unlockedGames: Math.min(10, state.unlockedGames + 1),
      };
    },

    // Guarda análisis completo del CV (contacto, experiencia, educación, etc.)
    saveCvAnalysis(state, action: PayloadAction<CvAnalysis>) {
      const analysis = action.payload;
      if (import.meta?.env?.DEV) {
        console.log('🔍 DEBUG - Reducer saveCvAnalysis ejecutado con payload:', analysis);
      }

      const newState = {
        ...state,
        cvAnalysis: analysis,
        unlockedGames: Math.min(10, state.unlockedGames + 1),
      };

      if (import.meta?.env?.DEV) {
        console.log('🔍 DEBUG - Nuevo estado después de saveCvAnalysis:', newState);
      }

      return newState;
    },

    // Desbloquea siguiente minijuego
    unlockNextGame(state) {
      if (state.unlockedGames < 10) {
        state.unlockedGames += 1;
      }
    },

    // Guarda habilidades blandas evaluadas
    saveSoftSkills(state, action: PayloadAction<SoftSkillResult[]>) {
      // Fusionar por nombre de habilidad para conservar el histórico de minijuegos
      const incoming = action.payload || [];
      const bySkill: Record<string, SoftSkillResult> = {};

      // Incluir existentes primero
      for (const existing of state.softSkills || []) {
        if (existing && existing.skill) {
          bySkill[existing.skill] = existing;
        }
      }

      // Mezclar entradas nuevas, priorizando el mayor score
      for (const s of incoming) {
        if (!s || !s.skill) continue;
        const prev = bySkill[s.skill];
        if (!prev || (typeof s.score === 'number' && s.score > (prev.score ?? 0))) {
          bySkill[s.skill] = s;
        }
      }

      state.softSkills = Object.values(bySkill);
    },

    // Registra decisiones tomadas durante escenas
    addSceneDecision(state, action: PayloadAction<UserDecision>) {
      const sceneId = action.payload.sceneId;
      const existingIndex: number = state.logs.findIndex(
        (log: SceneLog) => log.sceneId === String(sceneId),
      );
      const existingLog = state.logs[existingIndex];

      if (existingLog) {
        existingLog.decisions.push(action.payload);
      } else {
        state.logs.push({
          sceneId: String(sceneId),
          decisions: [action.payload],
          totalSteps: 5,
          totalTime: 300,
          averageConfidence:
            action.payload.skillImpacts[action.payload.optionText] || 0.6,
          emotionalTrend: ['positivo', 'neutro'] as (
            | 'positivo'
            | 'neutro'
            | 'negativo'
          )[],
          accessibilityUsed: !!state.accessibilitySettings,
          accessibilitySettings: state.accessibilitySettings,
        });
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
      // Validación del estado antes de procesar usando utilidades especializadas
      const validSkills = filterValidSoftSkills(state.softSkills);

      if (validSkills.length === 0) {
        if (import.meta?.env?.MODE !== 'production') {
          // eslint-disable-next-line no-console
          console.warn('generateFinalReport: No hay softSkills válidos para generar el informe');
        }
        return;
      }

      const totalSoftSkills = validSkills.length;
      const highSkills = validSkills.filter(skill => skill.level === 'alto').length;
      const mediumSkills = validSkills.filter(skill => skill.level === 'medio').length;
      const lowSkills = validSkills.filter(skill => skill.level === 'bajo').length;

      let employabilityScore = 0;
      if (totalSoftSkills > 0) {
        employabilityScore = Math.round(
          ((highSkills * 100 + mediumSkills * 70 + lowSkills * 30) / totalSoftSkills)
        );
      }

      // Ajuste según el CV
      const cvScore = state.cvAnalysis
        ? (
          state.cvAnalysis.structure_score +
          state.cvAnalysis.coherence_score +
          state.cvAnalysis.key_info_score +
          state.cvAnalysis.clarity_score +
          state.cvAnalysis.style_score
        ) / 5
        : undefined;
      if (typeof cvScore === 'number' && cvScore < 3) {
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
        softSkills: validSkills,
        cvAnalysis: state.cvAnalysis,
        preferences: state.jobPreferences as JobPreference,
        hasDisabilityCert: state.hasDisabilityCert,
      });
      // Flatten recommendations object into a string array with proper null/undefined handling
      const recommendations: string[] = [
        ...(recommendationsObj && Array.isArray(recommendationsObj.roles) ? recommendationsObj.roles.map(role => `Rol recomendado: ${role}`) : []),
        ...(recommendationsObj && Array.isArray(recommendationsObj.resources) ? recommendationsObj.resources.map(resource => `Recurso sugerido: ${resource}`) : []),
        ...(recommendationsObj && Array.isArray(recommendationsObj.cvImprovements) ? recommendationsObj.cvImprovements.map(improvement => `Mejora de CV: ${improvement}`) : []),
        ...(recommendationsObj && Array.isArray(recommendationsObj.nextSteps) ? recommendationsObj.nextSteps.map(step => `Próximo paso: ${step}`) : []),
      ];

      // Actualiza el estado del informe
      state.report = {
        userId: '',
        firstName: state.firstName,
        lastName: state.lastName,
        softSkills: validSkills,
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
  // Validación de parámetros de entrada usando utilidades especializadas
  const validSkills = filterValidSoftSkills(params.softSkills);

  if (validSkills.length === 0) {
    if (import.meta?.env?.MODE !== 'production') {
      // eslint-disable-next-line no-console
      console.warn('getRecommendationsFromProfile: No hay softSkills válidos');
    }
    return {
      roles: [],
      resources: [],
      cvImprovements: [],
      nextSteps: ['Completar todos los juegos', 'Actualizar tu CV', 'Revisar tus preferencias'],
    };
  }

  const roles: string[] = [];
  const resources: string[] = [];
  const cvImprovements: string[] = [];
  const nextSteps: string[] = [];

  // Ejemplo de lógica básica – puedes expandir esto desde backend o IA
  if (validSkills.some(skill => skill.level === 'alto')) {
    roles.push('Desarrollador frontend');
    roles.push('Soporte técnico');
    resources.push('Platzi');
    resources.push('Microsoft Learn');
  }

  // Validación segura de cvAnalysis
  if (params.cvAnalysis) {
    const { corrections = [], reordering_suggestions = [] } = params.cvAnalysis;
    const validCvImprovements = [...corrections, ...reordering_suggestions].filter(
      item => item && item.trim().length > 0
    );
    cvImprovements.push(...validCvImprovements);
  }

  // Siempre agregar pasos básicos
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
