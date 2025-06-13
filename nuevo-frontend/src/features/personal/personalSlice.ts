// src/features/personal/personalSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface PersonalState {
  firstName: string
  lastName: string
  email: string
  whatsapp: string

  // texto libre, no array
  jobPreferences: string  

  workMode: 'remoto' | 'presencial' | 'híbrido'
  availability: 'mañana' | 'tarde' | 'completa'

  // debe coincidir con PrefData
  startDate: 'inmediata' | '15_días' | '1_mes' | 'más_de_1_mes'

  willingToRelocate: boolean
  hasDisabilityCert: boolean

  // ← Nuevo campo para guardar el análisis del CV
  cvAnalysis?: CvAnalysis
}

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

  cvAnalysis: undefined, // sin análisis inicialmente
}

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
    // ← Nueva acción para guardar el análisis del CV
    saveCvAnalysis(
      state,
      action: PayloadAction<string>
    ) {
      state.cvAnalysis = action.payload
    },
  },
})

export const { saveContact, savePreferences, saveCvAnalysis } = personalSlice.actions
export default personalSlice.reducer
