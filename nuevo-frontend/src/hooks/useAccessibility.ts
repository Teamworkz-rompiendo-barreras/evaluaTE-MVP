// src/hooks/useAccessibility.ts
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import type { RootState } from "../app/store";
import { toggleContrast, setFontScale } from "../app/accessibilitySlice";

export function useAccessibility() {
  const dispatch = useDispatch();
  const { contrastLevel, fontScale } = useSelector(
    (state: RootState) => state.accessibility
  );

  // Efecto: aplica la clase y la escala de fuente en <html>
  useEffect(() => {
    const html = document.documentElement;

    // Ajusta la clase de contraste según el nivel
    if (contrastLevel === 'alto' || contrastLevel === 'muy-alto') {
      html.classList.add("high-contrast");
    } else {
      html.classList.remove("high-contrast");
    }

    // Ajusta la escala de fuente
    html.style.fontSize = `${fontScale}%`;
  }, [contrastLevel, fontScale]);

  return {
    contrastLevel,
    fontScale,
    toggleContrast: () => dispatch(toggleContrast()),
    setFontScale: (scale: number) => dispatch(setFontScale(scale)),
  };
}