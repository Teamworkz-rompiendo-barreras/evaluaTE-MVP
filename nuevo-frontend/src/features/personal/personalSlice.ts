// src/features/personal/personalSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

// 1) Interfaz para el análisis de CV
export interface CvAnalysis {
  score: number
  strengths: string[]
  weaknesses: string[]
}

// 2) Estado de usuario con campo de progreso
export interface PersonalState {
  firstName: string
  lastName: string
  email: string
  whatsapp: string

  jobPreferences: string  // texto libre, no array
  workMode: 'remoto' | 'presencial' | 'híbrido'
  availability: 'mañana' | 'tarde' | 'completa'
  startDate: 'inmediata' | '15_días' | '1_mes' | 'más_de_1_mes'

  willingToRelocate: boolean
  hasDisabilityCert: boolean

  // Campo para guardar el análisis del CV (opcional)
  cvAnalysis?: CvAnalysis

  // Campo para el progreso de minijuegos
  unlockedGames: number
}

// 3) Valores iniciales
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

  unlockedGames: 1, // Solo el primer minijuego desbloqueado al inicio
}

// 4) Slice con todas las acciones, incluido el progreso de minijuegos
const personalSlice = createSlice({
  name: 'personal',
  initialState,
  reducers: {
    saveContact(
      state,
      action: PayloadAction<
        Pick<PersonalState, 'firstName' | 'lastName' | 'email' | 'whatsapp'>
      >
    ) {
      Object.assign(state, action.payload)
    },
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
      Object.assign(state, action.payload)
    },
    // Acción para guardar el análisis del CV
    saveCvAnalysis(state, action: PayloadAction<CvAnalysis>) {
      state.cvAnalysis = action.payload
    },
    // Acción para desbloquear el siguiente minijuego
    unlockNextGame(state) {
      if (state.unlockedGames < 10) {
        state.unlockedGames += 1;
      }
    },
  },
})

export const { saveContact, savePreferences, saveCvAnalysis, unlockNextGame } = personalSlice.actions
export default personalSlice.reducer
