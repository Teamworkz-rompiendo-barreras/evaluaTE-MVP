// src/app/accessibilitySlice.ts
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface AccessibilityState {
  easyReadingMode: boolean
  audioAssistiveMode: boolean
  showPictograms: boolean
  contrastLevel: 'normal' | 'alto' | 'muy-alto'
  fontScale: number
}

const initialState: AccessibilityState = {
  easyReadingMode: false,
  audioAssistiveMode: false,
  showPictograms: false,
  contrastLevel: 'normal',
  fontScale: 100,
}

export const accessibilitySlice = createSlice({
  name: 'accessibility',
  initialState,
  reducers: {
    toggleEasyReadingMode: (state) => {
      state.easyReadingMode = !state.easyReadingMode
    },
    toggleAudioAssistiveMode: (state) => {
      state.audioAssistiveMode = !state.audioAssistiveMode
    },
    setShowPictograms: (state, action) => {
      state.showPictograms = action.payload
    },
    setContrastLevel: (state, action) => {
      state.contrastLevel = action.payload
    },
    setFontScale: (state, action) => {
      state.fontScale = action.payload
    }
  }
})

export const {
  toggleEasyReadingMode,
  toggleAudioAssistiveMode,
  setShowPictograms,
  setContrastLevel,
  setFontScale,
} = accessibilitySlice.actions