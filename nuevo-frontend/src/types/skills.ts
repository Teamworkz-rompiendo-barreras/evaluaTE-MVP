// src/types/skills.ts
import type { CvAnalysis } from './report';

/**
 * Resultado de evaluación de habilidades blandas
 */
export interface SoftSkillResult {
  /**
   * Nombre de la habilidad (ej: Toma de decisiones)
   */
  skill: string;

  /**
   * Nivel evaluado (Bajo / Medio / Alto)
   */
  level: 'Bajo' | 'Medio' | 'Alto';

  /**
   * Porcentaje de confianza (0.3 - 1)
   */
  confidence: number;

  /**
   * Descripción del nivel alcanzado
   */
  feedback?: string;

  /**
   * Registro de interacciones durante esta evaluación
   */
  interactions: UserDecision[];
}

/**
 * Registro de decisión tomada por el usuario
 */
export interface UserDecision {
  /**
   * ID de la escena
   */
  sceneId: number;

  /**
   * Índice del paso dentro de la escena
   */
  stepIndex: number;

  /**
   * Texto de la opción elegida
   */
  optionText: string;

  /**
   * Indica si la decisión fue correcta
   */
  isCorrect: boolean;

  /**
   * Impacto en las habilidades blandas
   */
  skillImpacts: Record<string, number>;

  /**
   * Marca de tiempo de la decisión
   */
  timestamp: string;

  /**
   * Información del navegador y dispositivo
   */
  userAgent: string;

  /**
   * Resolución de la pantalla
   */
  screenResolution: string;
}

/**
 * Log detallado de juego para IA
 */
export interface GameDecisionLog {
  /**
   * ID de la escena
   */
  sceneId: number;

  /**
   * Decisiones tomadas por el usuario
   */
  decisions: UserDecision[];

  /**
   * Total de pasos en la escena
   */
  totalSteps: number;

  /**
   * Tiempo total en la escena (en segundos)
   */
  totalTime: number;

  /**
   * Promedio de confianza en las decisiones
   */
  averageConfidence: number;

  /**
   * Tendencia emocional a lo largo de la escena
   */
  emotionalTrend: ('positivo' | 'neutro' | 'negativo')[];

  /**
   * Indica si se usaron adaptaciones de accesibilidad
   */
  accessibilityUsed: boolean;

  /**
   * Configuración de accesibilidad usada durante la escena
   */
  accessibilitySettings?: AccessibilitySettings;
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
 * Preferencias laborales del candidato
 */
export interface JobPreference {
  /**
   * Sectores o áreas de interés
   */
  areas: string[];

  /**
   * Necesidades específicas
   */
  needs: string[];

  /**
   * Modo de trabajo preferido
   */
  workMode?: 'remoto' | 'presencial' | 'híbrido';

  /**
   * Disponibilidad horaria
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
   * Configuración de accesibilidad usada durante la gamificación
   */
  accessibilitySettings?: AccessibilitySettings;
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
  fullName: string;

  /**
   * Habilidades blandas evaluadas
   */
  softSkills: SoftSkillResult[];

  /**
   * Puntaje global de empleabilidad (0-100)
   */
  employabilityScore: number;

  /**
   * Nivel de empleabilidad (bajo/media/alta)
   */
  level: 'Baja empleabilidad' | 'Empleabilidad media' | 'Alta empleabilidad';

  /**
   * Score ajustado después de análisis del CV
   */
  adjustedScore: number;

  /**
   * Preferencias laborales del candidato
   */
  jobPreferences: JobPreference;

  /**
   * Análisis del CV cargado
   */
  cvAnalysis?: CvAnalysis;

  /**
   * Fecha de creación del informe
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
   * Recomendaciones personalizadas
   */
  recommendations: {
    /**
     * Roles recomendados
     */
    roles: string[];

    /**
     * Recursos sugeridos (formaciones, portales, etc.)
     */
    resources: string[];

    /**
     * Mejoras sugeridas para el CV
     */
    cvImprovements: string[];

    /**
     * Próximos pasos sugeridos
     */
    nextSteps: string[];
  };
}