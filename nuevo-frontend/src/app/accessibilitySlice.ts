// src/app/accessibilitySlice.ts
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface AccessibilityState {
  easyReadingMode: boolean;
  audioAssistiveMode: boolean;
  showPictograms: boolean;
  contrastLevel: 'normal' | 'alto' | 'muy-alto';
  fontScale: number;
  fontFamily: 'sans' | 'dyslexic' | 'readable';
}

const initialState: AccessibilityState = {
  easyReadingMode: false,
  audioAssistiveMode: false,
  showPictograms: false,
  contrastLevel: 'normal',
  fontScale: 100,
  fontFamily: 'sans',
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
    setFontFamily: (state, action: PayloadAction<'sans' | 'dyslexic' | 'readable'>) => {
      state.fontFamily = action.payload;
    },
    toggleContrast: (state) => {
      const levels: ('normal' | 'alto' | 'muy-alto')[] = ['normal', 'alto', 'muy-alto'];
      const currentIndex = levels.indexOf(state.contrastLevel);
      const nextIndex = (currentIndex + 1) % levels.length;
      const nextLevel = levels[nextIndex];
      if (nextLevel) {
        state.contrastLevel = nextLevel;
      }
    },
  },
});

export const {
  toggleEasyReadingMode,
  toggleAudioAssistiveMode,
  setShowPictograms,
  setContrastLevel,
  setFontScale,
  setFontFamily,
  toggleContrast,
} = accessibilitySlice.actions;

export default accessibilitySlice.reducer;