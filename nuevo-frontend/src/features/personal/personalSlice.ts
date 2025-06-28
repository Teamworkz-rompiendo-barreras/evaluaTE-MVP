// src/features/personal/personalSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

// Tipos desde tu carpeta compartida de tipos
import {
  CvAnalysis,
  SoftSkillResult,
  EmployabilityReport,
} from '../../types/skills'

// Estado principal del usuario
export interface PersonalState {
  firstName: string
  lastName: string
  email: string
  whatsapp: string

  jobPreferences: string
  workMode: 'remoto' | 'presencial' | 'híbrido'
  availability: 'mañana' | 'tarde' | 'completa'
  startDate: 'inmediata' | '15_días' | '1_mes' | 'más_de_1_mes'

  willingToRelocate: boolean
  hasDisabilityCert: boolean

  cvFile: File | null // Archivo del CV
  cvAnalysis?: CvAnalysis // Análisis del CV
  softSkills: SoftSkillResult[] // Habilidades blandas evaluadas
  unlockedGames: number // Juegos desbloqueados (máx 10)
  report?: EmployabilityReport // Informe final con todas las habilidades
}

// Estado inicial por defecto
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
}

// Definición del slice
const personalSlice = createSlice({
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
      }
    },

    // Guarda preferencias laborales
    savePreferences(
      state,
      action: PayloadAction<
        Pick<
          PersonalState,
          | 'jobPreferences'
          | 'workMode'
          | 'availability'
          | 'startDate'
          | 'willingToRelocate'
          | 'hasDisabilityCert'
        >
      >
    ) {
      return {
        ...state,
        ...action.payload,
      }
    },

    // Guarda el archivo del CV
    saveCV(state, action: PayloadAction<File>) {
      state.cvFile = action.payload
    },

    // Guarda el análisis del CV procesado
    saveCvAnalysis(state, action: PayloadAction<CvAnalysis>) {
      state.cvAnalysis = action.payload
    },

    // Desbloquea el siguiente minijuego
    unlockNextGame(state) {
      if (state.unlockedGames < 10) {
        state.unlockedGames += 1
      }
    },

    // Guarda habilidades blandas evaluadas
    saveSoftSkills(state, action: PayloadAction<SoftSkillResult[]>) {
      state.softSkills = action.payload
    },

    // Genera informe final basado en CV + soft skills
    generateFinalReport(state) {
      const totalSoftSkills = state.softSkills.length
      const highSkills = state.softSkills.filter(skill => skill.level === 'Alto').length
      const mediumSkills = state.softSkills.filter(skill => skill.level === 'Medio').length
      const lowSkills = state.softSkills.filter(skill => skill.level === 'Bajo').length

      let employabilityScore = 0
      if (totalSoftSkills > 0) {
        employabilityScore = Math.round(
          ((highSkills * 100 + mediumSkills * 70 + lowSkills * 30) / totalSoftSkills
        )
      }

      // Ajustes según el CV
      if (state.cvAnalysis?.score && state.cvAnalysis.score < 60) {
        employabilityScore = Math.max(20, employabilityScore - 10)
      }

      state.report = {
        userId: 'user-1234', // Esto debería venir de auth
        fullName: `${state.firstName} ${state.lastName}`,
        softSkills: state.softSkills,
        employabilityScore,
        jobPreferences: state.jobPreferences ? { areas: [state.jobPreferences] } : { areas: [] },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        completedGames: Array.from({ length: state.unlockedGames }, (_, i) => i + 1),
      }
    },
  },
})

// Exportamos las acciones
export const {
  saveContact,
  savePreferences,
  saveCV,
  saveCvAnalysis,
  unlockNextGame,
  saveSoftSkills,
  generateFinalReport,
} = personalSlice.actions

export default personalSlice.reducer