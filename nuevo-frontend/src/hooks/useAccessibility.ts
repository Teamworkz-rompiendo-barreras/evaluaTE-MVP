// src/hooks/useAccessibility.ts
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import type { RootState } from "../app/store";
import { toggleContrast, setFontScale } from "../app/accessibilitySlice";

export const useAccessibility = () => {
  const dispatch = useDispatch();
  const accessibility = useSelector((state: RootState) => state.accessibility);

  // Efecto: aplica la clase y la escala de fuente en <html>
  useEffect(() => {
    const html = document.documentElement;

    // Ajusta la clase de contraste según el nivel
    if (accessibility.contrastLevel === 'alto' || accessibility.contrastLevel === 'muy-alto') {
      html.classList.add("high-contrast");
    } else {
      html.classList.remove("high-contrast");
    }

    // Ajusta la escala de fuente
    html.style.fontSize = `${accessibility.fontScale}%`;
  }, [accessibility.contrastLevel, accessibility.fontScale]);

  const setContrastLevel = (level: 'normal' | 'high') => {
    dispatch(toggleContrast());
  };

  const toggleContrastHandler = () => {
    dispatch(toggleContrast());
  };

  const setFontScaleHandler = (scale: number) => {
    dispatch(setFontScale(scale));
  };

  const setVisualHelp = (enabled: boolean) => {
    // Implementation needed
  };

  const setTimeExtensions = (enabled: boolean) => {
    // Implementation needed
  };

  return {
    ...accessibility,
    setContrastLevel,
    setVisualHelp,
    setTimeExtensions,
    toggleContrast: toggleContrastHandler,
    setFontScale: setFontScaleHandler,
  };
};