// src/features/personal/personalSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

// 1) Definimos la interfaz para el análisis de CV
export interface CvAnalysis {
  score: number
  strengths: string[]
  weaknesses: string[]
}

// 2) Estado de usuario con nuevo campo opcional cvAnalysis
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

  // Nuevo campo para guardar el análisis del CV (opcional)
  cvAnalysis?: CvAnalysis
}

// 3) Valores iniciales, cvAnalysis arranca undefined
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
}

// 4) Slice con nueva acción saveCvAnalysis
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
    saveCvAnalysis(state, action: PayloadAction<CvAnalysis>) {
      state.cvAnalysis = action.payload
    },
  },
})

export const { saveContact, savePreferences, saveCvAnalysis } = personalSlice.actions
export default personalSlice.reducer
