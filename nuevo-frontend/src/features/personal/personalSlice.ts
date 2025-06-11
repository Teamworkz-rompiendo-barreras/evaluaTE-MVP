// src/features/personal/personalSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface PersonalState {
  firstName: string
  lastName: string
  email: string
  whatsapp: string
  jobPreferences: string
  workMode: 'remoto' | 'presencial' | 'híbrido'
  availability: 'mañana' | 'tarde' | 'completa'
  startDate: string
  willingToRelocate: boolean
  hasDisabilityCert: boolean
}

const initialState: PersonalState = {
  firstName: '',
  lastName: '',
  email: '',
  whatsapp: '',
  jobPreferences: '',
  workMode: 'remoto',
  availability: 'completa',
  startDate: '',
  willingToRelocate: false,
  hasDisabilityCert: false,
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
  },
})

export const { saveContact, savePreferences } = personalSlice.actions
export default personalSlice.reducer
