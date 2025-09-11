// src/types/preferences.ts

import type { CvAnalysis } from './report';
/**
 * Análisis del CV cargado (estructura legacy)
 */
export interface LegacyCvAnalysis {
  // Campos básicos del análisis
  strengths: string[];
  weaknesses: string[];
  feedback?: string;
  structure?: string;
  coherence?: string;
  experience?: string;
  skills?: string[];
  education?: string[];
  alerts?: string[];
  
  // Campos estructurados del CV extraídos por IA
  cv_structured?: {
    candidate?: string | Record<string, unknown>;
    contact?: CvContact;
    experience?: CvExperienceItem[];
    education?: CvEducationItem[];
    languages?: CvLanguageItem[];
    skills?: CvSkillItem[];
    summary?: string;
  };
  
  // Campos directos del CV
  candidate?: string | Record<string, unknown>;
  contact?: CvContact;
  experience_detailed?: CvExperienceItem[];
  education_detailed?: CvEducationItem[];
  languages?: CvLanguageItem[];
  periods?: string[];
  highlights?: string[];
  volunteering?: Array<Record<string, unknown>>;
  
  // Campos de análisis estructurado
  cv_analysis_structured?: Record<string, unknown>;
  raw_text?: string;
  layout_sections?: Record<string, unknown>;
  ai_analysis?: Record<string, unknown>;
  basic_hints?: Record<string, unknown>;
  provenance?: Record<string, unknown>;
}

export interface CvContact {
  emails?: string[];
  phones?: string[];
  location?: string;
  linkedin?: string;
}

export interface CvExperienceItem {
  position?: string;
  title?: string;
  company?: string;
  organization?: string;
  organisation?: string;
  start_date?: string;
  end_date?: string;
  current?: boolean;
  description?: string;
}

export interface CvEducationItem {
  degree?: string;
  title?: string;
  institution?: string;
  school?: string;
  start_date?: string;
  end_date?: string;
}

export interface CvLanguageItem {
  language?: string;
  name?: string;
  level?: string;
}

export type CvSkillItem = { name?: string; tool?: string } | string;

/**
 * Preferencias laborales del candidato
 */
export interface JobPreference {
  /**
   * Sectores o áreas de interés del candidato
   * Ejemplos: "Logística", "Atención al cliente", "Tecnología"
   */
  areas: string[];

  /**
   * Necesidades específicas o apoyos requeridos
   * Ejemplo: "Trabajo en entorno tranquilo", "Acceso a luz natural"
   */
  needs: string[];

  /**
   * Modo de trabajo preferido
   * remoto, presencial o híbrido
   */
  workMode?: 'remoto' | 'presencial' | 'híbrido';

  /**
   * Disponibilidad horaria
   * mañana, tarde o completa
   */
  availability?: 'mañana' | 'tarde' | 'completa';

  /**
   * ¿Está dispuesto a mudarse si es necesario?
   */
  willingToRelocate: boolean;

  /**
   * ¿Tiene certificado de discapacidad?
   */
  hasDisabilityCert: boolean;

  /**
   * Idiomas dominados (opcional)
   */
  languages?: string[];

  /**
   * Tipo de jornada deseada (opcional)
   */
  scheduleType?: 'media' | 'completa' | 'adaptativa';

  /**
   * Adaptaciones activadas durante la gamificación
   */
  accessibilitySettings?: AccessibilitySettings;
}

export interface SoftSkillResult {
  skill: string;
  score: number;
  level: 'bajo' | 'medio' | 'alto';
  confidence: number;
}
/**
 * Configuración de accesibilidad según elecciones del usuario
 */
export interface AccessibilitySettings {
  /**
   * Si usa modo lectura fácil
   */
  easyReadingMode: boolean;

  /**
   * Si ha activado ayuda auditiva
   */
  audioAssistiveMode: boolean;

  /**
   * Si muestra pictogramas visuales
   */
  showPictograms: boolean;

  /**
   * Nivel de contraste activo
   */
  contrastLevel: 'normal' | 'alto' | 'muy-alto';

  /**
   * Escala de fuente
   */
  fontScale: number;
}

/**
 * Informe final de empleabilidad
 */
export interface EmployabilityReport {
  /**
   * ID único del usuario
   */
  userId: string;

  /**
   * Nombre completo del candidato
   */
  firstName: string
  lastName: string

  /**
   * Habilidades blandas evaluadas
   */
  softSkills: SoftSkillResult[];

  /**
   * Puntaje global de empleabilidad (0-100)
   */
  employabilityScore: number;

  /**
   * Nivel de empleabilidad (bajo, medio, alto)
   */
  level: 'bajo' | 'medio' | 'alto';

  /**
   * Preferencias laborales del candidato
   */
  jobPreferences: JobPreference;

  /**
   * Análisis del CV cargado
   */
  cvAnalysis?: CvAnalysis;

  /**
   * Fecha de generación del informe
   */
  createdAt: string;

  /**
   * Última fecha de modificación
   */
  updatedAt: string;

  /**
   * Juegos completados hasta ahora
   */
  completedGames: number[];

  /**
   * Score ajustado después de análisis del CV
   */
  adjustedScore: number;
  recommendations: string[]
}