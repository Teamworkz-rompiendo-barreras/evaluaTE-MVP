// nuevo-frontend/src/features/personal/personalSlice.ts

import { createSlice, PayloadAction, Draft } from "@reduxjs/toolkit";
import type { CvAnalysis, JobPreference, AccessibilitySettings, EmployabilityReport, SoftSkillResult } from "@/types/preferences";

const initialState: {
  firstName: string;
  lastName: string;
  contactEmail: string;
  contactPhone: string;
  cvFile: { fileName: string; fileContent: string } | null;
  cvAnalysis: CvAnalysis | null;
  jobPreferences: JobPreference | null;
  registrationStep: 'contact' | 'preferences' | 'games' | 'uploadCV' | 'resultados';
  softSkillsScores: SoftSkillResult[];
  employabilityScore: number;
  level: 'Baja empleabilidad' | 'Empleabilidad media' | 'Alta empleabilidad';
  adjustedScore: number;
  finalReport: EmployabilityReport | null;
  unlockedGames: number;
  workMode?: 'remoto' | 'presencial' | 'híbrido';
  availability?: 'mañana' | 'tarde' | 'completa';
  willingToRelocate: boolean;
  hasDisabilityCert: boolean;
} = {
  firstName: "",
  lastName: "",
  contactEmail: "",
  contactPhone: "",
  cvFile: null,
  cvAnalysis: null,
  jobPreferences: null,
  registrationStep: 'contact',
  softSkillsScores: [],
  employabilityScore: 0,
  level: 'Baja empleabilidad',
  adjustedScore: 0,
  finalReport: null,
  unlockedGames: 0,
  willingToRelocate: false,
  hasDisabilityCert: false,
};

export const personalSlice = createSlice({
  name: 'personal',
  initialState,
  reducers: {
    saveContact: (state, action: PayloadAction<{ firstName: string; lastName: string; contactEmail: string; contactPhone: string }>) => {
      state.firstName = action.payload.firstName;
      state.lastName = action.payload.lastName;
      state.contactEmail = action.payload.contactEmail;
      state.contactPhone = action.payload.contactPhone;
    },
    savePreferences: (state, action: PayloadAction<JobPreference>) => {
      state.jobPreferences = action.payload;
      state.workMode = action.payload.workMode;
      state.availability = action.payload.availability;
      state.willingToRelocate = action.payload.willingToRelocate;
      state.hasDisabilityCert = action.payload.hasDisabilityCert;
    },
    saveCV: (state, action: PayloadAction<{ fileName: string; fileContent: string }>) => {
      state.cvFile = action.payload;
    },
    analyzeCV: (state, action: PayloadAction<CvAnalysis>) => {
      state.cvAnalysis = action.payload;
    },
    generateFinalReport: (state, action: PayloadAction<Draft<EmployabilityReport>>) => {
      const employabilityScore = action.payload.employabilityScore;
      const adjustedScore = action.payload.adjustedScore;
      const levelLabel = employabilityScore >= 80 ? 'Alta empleabilidad' : employabilityScore >= 50 ? 'Empleabilidad media' : 'Baja empleabilidad';
      const level: 'alto' | 'medio' | 'bajo' =
        levelLabel === 'Alta empleabilidad'
          ? 'alto'
          : levelLabel === 'Empleabilidad media'
          ? 'medio'
          : 'bajo';

      // Actualiza el estado del informe
      state.finalReport = {
        userId: action.payload.userId,
        firstName: state.firstName,
        lastName: state.lastName,
        softSkills: action.payload.softSkills,
        employabilityScore: employabilityScore,
        jobPreferences: action.payload.jobPreferences,
        cvAnalysis: action.payload.cvAnalysis,
        createdAt: action.payload.createdAt,
        updatedAt: action.payload.updatedAt,
        completedGames: action.payload.completedGames,
        level: level,
        adjustedScore: adjustedScore,
        recommendations: action.payload.recommendations,
      };
    },
    updateSoftSkillsScores: (state, action: PayloadAction<SoftSkillResult[]>) => {
      state.softSkillsScores = action.payload;
    },
    updateEmployabilityScore: (state, action: PayloadAction<number>) => {
      state.employabilityScore = action.payload;
    },
    updateLevel: (state, action: PayloadAction<'Baja empleabilidad' | 'Empleabilidad media' | 'Alta empleabilidad'>) => {
      state.level = action.payload;
    },
    updateAdjustedScore: (state, action: PayloadAction<number>) => {
      state.adjustedScore = action.payload;
    },
    unlockGame: (state) => {
      state.unlockedGames += 1;
    },
  },
});

export const {
  saveContact,
  savePreferences,
  saveCV,
  analyzeCV,
  generateFinalReport,
  updateSoftSkillsScores,
  updateEmployabilityScore,
  updateLevel,
  updateAdjustedScore,
  unlockGame,
} = personalSlice.actions;

export default personalSlice.reducer;