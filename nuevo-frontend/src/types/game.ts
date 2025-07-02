// src/types/game.ts

import type { SoftSkillResult } from '@/types/preferences';

/**
 * Opción seleccionada por el usuario en una escena
 */
export interface SceneOption {
  text: string;
  isCorrect?: boolean; // Hacemos isCorrect opcional
  skillImpact?: Record<string, number>; // Ej: {'Toma de decisiones': 0.9}
  feedback?: string; // Mensaje tras elegir esta opción
  requiresAdaptation?: boolean; // Si se activa algún ajuste de accesibilidad
}

/**
 * Paso o momento dentro de una escena
 */
export interface GameStep {
  text: string;
  image?: string;
  audio?: string; // Para usuarios que prefieren audios
  options: SceneOption[];
  timeLimit?: number; // Límite de tiempo (opcional)
  autoProceed?: boolean; // Avanzar automáticamente tras elección
}

/**
 * Escena completa del minijuego
 */
export interface GameScene {
  id: number;
  title: string;
  description: string;
  steps: GameStep[];
  softSkillsTracked: string[]; // Habilidades evaluadas en esta escena
  estimatedTime?: number; // Tiempo estimado en minutos
  difficulty?: 'fácil' | 'media' | 'alta';
  accessibilityOptions?: {
    showPictograms: boolean;
    audioAssistiveMode: boolean;
    contrastLevel: 'normal' | 'alto' | 'muy-alto';
  };
}

export type UserDecision = {
  // Define the properties of UserDecision here, for example:
  sceneId: string;
  optionText: string;
  skillImpacts: Record<string, number>;
  // Add other fields as needed
};

/**
 * Respuesta del API al pedir una escena
 */
export interface GameSceneResponse extends GameScene {}