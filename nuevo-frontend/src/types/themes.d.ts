// src/types/themes.d.ts

/**
 * Paleta de colores personalizada
 */
export type ColorPalette = {
  primary: string;
  secondary: string;
  accent: string;
  neutral: {
    light: string;
    DEFAULT: string;
    dark: string;
  };
  success: string;
  warning: string;
  error: string;
  info: string;
};

/**
 * Tipos de tamaño de texto
 */
export type TextSize = {
  xs: string
  sm: string
  base: string
  lg: string
  xl: string
  '2xl': string
}

/**
 * Tipos de espaciado (padding, margin)
 */
export type Spacing = {
  '72': string
  '84': string
  '96': string
}

/**
 * Tipos de borde redondeado
 */
export type BorderRadius = {
  none: string
  sm: string
  DEFAULT: string
  md: string
  lg: string
  xl: string
  '2xl': string
  '3xl': string
  '4xl': string
}

/**
 * Tema completo del proyecto
 */
export type Theme = {
  colors: ColorPalette
  fontSize: TextSize
  spacing: Spacing
  borderRadius: BorderRadius
}