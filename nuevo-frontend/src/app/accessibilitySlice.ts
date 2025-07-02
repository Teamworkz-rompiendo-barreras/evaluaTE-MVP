// src/app/accessibilitySlice.ts
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface AccessibilityState {
  easyReadingMode: boolean;
  audioAssistiveMode: boolean;
  showPictograms: boolean;
  contrastLevel: 'normal' | 'alto' | 'muy-alto';
  fontScale: number;
}

const initialState: AccessibilityState = {
  easyReadingMode: false,
  audioAssistiveMode: false,
  showPictograms: false,
  contrastLevel: 'normal',
  fontScale: 100,
};

export const accessibilitySlice = createSlice({
  name: 'accessibility',
  initialState,
  reducers: {
    toggleEasyReadingMode: (state) => {
      state.easyReadingMode = !state.easyReadingMode;
    },
    toggleAudioAssistiveMode: (state) => {
      state.audioAssistiveMode = !state.audioAssistiveMode;
    },
    setShowPictograms: (state, action: PayloadAction<boolean>) => {
      state.showPictograms = action.payload;
    },
    setContrastLevel: (state, action: PayloadAction<'normal' | 'alto' | 'muy-alto'>) => {
      state.contrastLevel = action.payload;
    },
    setFontScale: (state, action: PayloadAction<number>) => {
      state.fontScale = action.payload;
    },
    toggleContrast: (state) => {
      const levels: ('normal' | 'alto' | 'muy-alto')[] = ['normal', 'alto', 'muy-alto'];
      const currentIndex = levels.indexOf(state.contrastLevel);
      const nextIndex = (currentIndex + 1) % levels.length;
      state.contrastLevel = levels[nextIndex];
    },
  },
});

export const {
  toggleEasyReadingMode,
  toggleAudioAssistiveMode,
  setShowPictograms,
  setContrastLevel,
  setFontScale,
  toggleContrast,
} = accessibilitySlice.actions;

export default accessibilitySlice.reducer;