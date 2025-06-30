// src/features/personal/personalSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

// Tipos compartidos
import {
  CvAnalysis,
  SoftSkillResult,
  EmployabilityReport,
} from '../../types/skills'
// Define JobPreference type locally since '../../types/preferences' is missing
export interface JobPreference {
  areas: string[]
  needs: string[]
  workMode: 'remoto' | 'presencial' | 'híbrido'
  availability: 'mañana' | 'tarde' | 'completa'
  // Add other fields as needed
}

// Estado principal del usuario
export interface PersonalState {
  firstName: string
  lastName: string
  email: string
  whatsapp: string

  jobPreferences: string | JobPreference // Puede ser cadena o objeto completo
  workMode: 'remoto' | 'presencial' | 'híbrido'
  availability: 'mañana' | 'tarde' | 'completa'
  startDate: 'inmediata' | '15_días' | '1_mes' | 'más_de_1_mes'

  willingToRelocate: boolean
  hasDisabilityCert: boolean

  cvFile: File | null
  cvAnalysis?: CvAnalysis
  softSkills: SoftSkillResult[]
  unlockedGames: number
  report?: EmployabilityReport
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
      const payload = action.payload

      // Si viene como string, lo convertimos a objeto JobPreference
      if (typeof payload.jobPreferences === 'string') {
        payload.jobPreferences = {
          areas: [payload.jobPreferences],
          needs: [],
          workMode: payload.workMode,
          availability: payload.availability,
        }
      }

      return {
        ...state,
        ...payload,
      }
    },

    // Guarda el archivo del CV
    saveCV(state, action: PayloadAction<File>) {
      state.cvFile = action.payload
    },

    // Guarda análisis del CV procesado
    saveCvAnalysis(state, action: PayloadAction<CvAnalysis>) {
      state.cvAnalysis = action.payload
    },

    // Desbloquea siguiente minijuego
    unlockNextGame(state) {
      if (state.unlockedGames < 10) {
        state.unlockedGames += 1
      }
    },

    // Guarda habilidades blandas evaluadas
    saveSoftSkills(state, action: PayloadAction<SoftSkillResult[]>) {
      state.softSkills = action.payload
    },

    // Genera informe final basado en todo el progreso
    generateFinalReport(state) {
      const totalSoftSkills = state.softSkills.length
      const highSkills = state.softSkills.filter(skill => skill.level === 'Alto').length
      const mediumSkills = state.softSkills.filter(skill => skill.level === 'Medio').length
      const lowSkills = state.softSkills.filter(skill => skill.level === 'Bajo').length

      let employabilityScore = 0
      if (totalSoftSkills > 0) {
        employabilityScore = Math.round(
          ((highSkills * 100 + mediumSkills * 70 + lowSkills * 30) / totalSoftSkills)
        )
      }

      // Ajustes según el CV
      if (state.cvAnalysis?.score && state.cvAnalysis.score < 60) {
        employabilityScore = Math.max(20, employabilityScore - 10)
      }

      // Actualiza el estado del informe
      state.report = {
        userId: 'user-1234', // Debe venir de autenticación real
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
              }
            : {
                ...state.jobPreferences,
                willingToRelocate: state.willingToRelocate,
                hasDisabilityCert: state.hasDisabilityCert,
              },
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