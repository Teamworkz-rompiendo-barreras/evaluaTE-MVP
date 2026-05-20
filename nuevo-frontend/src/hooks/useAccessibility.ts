// src/hooks/useAccessibility.ts
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import type { RootState } from "../app/store";
import { toggleContrast, setFontScale, setFontFamily } from "../app/accessibilitySlice";

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

    // Ajusta la familia de fuente según la selección
    const fontClasses = {
      sans: 'font-sans',
      dyslexic: 'font-dyslexic',
      readable: 'font-readable'
    };

    // Remover clases de fuente anteriores
    Object.values(fontClasses).forEach(className => {
      html.classList.remove(className);
    });

    // Agregar la clase de fuente seleccionada
    if (accessibility.fontFamily && fontClasses[accessibility.fontFamily as keyof typeof fontClasses]) {
      html.classList.add(fontClasses[accessibility.fontFamily as keyof typeof fontClasses]);
    } else {
      // Fallback a fuente estándar
      html.classList.add('font-sans');
    }

  }, [accessibility.contrastLevel, accessibility.fontScale, accessibility.fontFamily]);

  const setContrastLevel = (_level: 'normal' | 'high') => {
    dispatch(toggleContrast());
  };

  const toggleContrastHandler = () => {
    dispatch(toggleContrast());
  };

  const setFontScaleHandler = (scale: number) => {
    dispatch(setFontScale(scale));
  };

  const setFontFamilyHandler = (family: 'sans' | 'dyslexic' | 'readable') => {
    dispatch(setFontFamily(family));
  };

  const setVisualHelp = (_enabled: boolean) => {
    // Implementation needed
  };

  const setTimeExtensions = (_enabled: boolean) => {
    // Implementation needed
  };

  return {
    ...accessibility,
    setContrastLevel,
    setVisualHelp,
    setTimeExtensions,
    toggleContrast: toggleContrastHandler,
    setFontScale: setFontScaleHandler,
    setFontFamily: setFontFamilyHandler,
  };
};