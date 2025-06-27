// src/features/personal/personalSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

// Interfaz para análisis del CV
export interface CvAnalysis {
  score: number
  strengths: string[]
  weaknesses: string[]
}

// Interfaz por habilidad blanda evaluada
export interface SoftSkillResult {
  skill: string
  level: 'Bajo' | 'Medio' | 'Alto'
  confidence: number // puntuación entre 0 y 1
}

// Estado principal del usuario
export interface PersonalState {
  firstName: string
  lastName: string
  email: string
  whatsapp: string

  jobPreferences: string // Ej: "Desarrollo web"
  workMode: 'remoto' | 'presencial' | 'híbrido'
  availability: 'mañana' | 'tarde' | 'completa'
  startDate: 'inmediata' | '15_días' | '1_mes' | 'más_de_1_mes'

  willingToRelocate: boolean
  hasDisabilityCert: boolean

  cvAnalysis?: CvAnalysis // Análisis opcional del CV
  cvFile: File | null // 👈 Nuevo campo
  unlockedGames: number // Número de minijuegos desbloqueados
  softSkills?: SoftSkillResult[] // Habilidades blandas evaluadas
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

  cvAnalysis: undefined,
  cvFile: null, // 👈 Inicializamos el nuevo campo
  unlockedGames: 1, // Solo el primer juego disponible al inicio
  softSkills: undefined,
}

// Definición del slice
const personalSlice = createSlice({
  name: 'personal',
  initialState,
  reducers: {
    // Guarda datos personales (nombre, apellidos, contacto)
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

    // Guarda habilidades blandas evaluadas (desde minijuegos)
    saveSoftSkills(state, action: PayloadAction<SoftSkillResult[]>) {
      state.softSkills = action.payload
    },
  },
})

// Exportamos las acciones
export const {
  saveContact,
  savePreferences,
  saveCV, // 👈 Exportamos esta nueva acción
  saveCvAnalysis,
  unlockNextGame,
  saveSoftSkills,
} = personalSlice.actions

export default personalSlice.reducer