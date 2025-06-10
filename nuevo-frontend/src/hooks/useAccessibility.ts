// src/hooks/useAccessibility.ts
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import type { RootState } from "../app/store";
import { toggleContrast, setFontScale } from "../app/accessibilitySlice";

export function useAccessibility() {
  const dispatch = useDispatch();
  const { highContrast, fontScale } = useSelector(
    (state: RootState) => state.accessibility
  );

  // Efecto: aplica la clase y la escala de fuente en <html>
  useEffect(() => {
    const html = document.documentElement;
    if (highContrast) html.classList.add("high-contrast");
    else html.classList.remove("high-contrast");
    html.style.fontSize = `${fontScale}%`;
  }, [highContrast, fontScale]);

  return {
    highContrast,
    fontScale,
    toggleContrast: () => dispatch(toggleContrast()),
    setFontScale: (scale: number) => dispatch(setFontScale(scale)),
  };
}
