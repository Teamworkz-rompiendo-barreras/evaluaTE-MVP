// src/types/game-scene.ts

/**
 * Opción seleccionada por el usuario en una escena
 */
export interface SceneOption {
  text: string
  isCorrect?: boolean
  skillImpact?: Record<string, number> // Ej: {'Toma de decisiones': 0.9}
  feedback?: string // Mensaje tras elegir esta opción
  requiresAdaptation?: boolean // Si se activa algún ajuste de accesibilidad
}

/**
 * Paso o momento dentro de una escena
 */
export interface GameStep {
  text: string
  image?: string
  audio?: string // Para usuarios que prefieren audios
  options: SceneOption[]
  timeLimit?: number // Límite de tiempo (opcional)
  autoProceed?: boolean // Avanzar automáticamente tras elección
}

/**
 * Escena completa del minijuego
 */
export interface GameScene {
  id: number
  title: string
  steps: GameStep[]
  softSkillsTracked: string[] // Habilidades evaluadas en esta escena
  estimatedTime?: number // Tiempo estimado en minutos
  difficulty?: 'fácil' | 'media' | 'alta'
  accessibilityOptions?: {
    showPictograms: boolean
    audioAssistiveMode: boolean
    contrastLevel: 'normal' | 'alto' | 'muy-alto'
  }
}

/**
 * Registro de decisión tomada por el usuario
 */
export interface UserDecision {
  sceneId: number
  stepIndex: number
  optionText: string
  timestamp: string
  isCorrect: boolean
  skillImpacts: Record<string, number>
  userAgent: string // Datos del dispositivo
  screenResolution: string // Para análisis UX
}

/**
 * Historial de decisiones del usuario
 */
export interface UserDecisionHistory {
  decisions: UserDecision[]
  userId: string
  createdAt: string
  updatedAt: string
  completedGames: number[]
  preferencesAtStart: {
    areas: string[];
    needs: string[];
    workMode?: 'remoto' | 'presencial' | 'híbrido';
    availability?: 'mañana' | 'tarde' | 'completa';
    willingToRelocate: boolean;
    hasDisabilityCert: boolean;
    languages?: string[];
    scheduleType?: 'media' | 'completa' | 'adaptativa';
    accessibilitySettings?: {
      easyReadingMode: boolean;
      audioAssistiveMode: boolean;
      showPictograms: boolean;
      contrastLevel: 'normal' | 'alto' | 'muy-alto';
      fontScale: number;
    };
  };
  softSkillsAtEnd: Array<{
    skill: string;
    score: number;
    level: 'bajo' | 'medio' | 'alto';
  }>;
  employabilityScore: number // Puntaje global calculado
}