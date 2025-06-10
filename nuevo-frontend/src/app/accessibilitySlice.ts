// src/app/accessibilitySlice.ts
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface AccessibilityState {
  highContrast: boolean;
  fontScale: number; // en %, e.g. 100 = 100%
}

const initialState: AccessibilityState = {
  highContrast: false,
  fontScale: 100,
};

const accessibilitySlice = createSlice({
  name: "accessibility",
  initialState,
  reducers: {
    toggleContrast(state) {
      state.highContrast = !state.highContrast;
    },
    setFontScale(state, action: PayloadAction<number>) {
      state.fontScale = action.payload;
    },
  },
});

export const { toggleContrast, setFontScale } = accessibilitySlice.actions;
export default accessibilitySlice.reducer;
