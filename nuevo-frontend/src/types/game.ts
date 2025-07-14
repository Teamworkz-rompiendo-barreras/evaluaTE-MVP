// src/types/game.ts

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
  id: string;
  title: string;
  description: string;
  type: 'choice' | 'drag-drop' | 'text-input' | 'audio' | 'visual-exploration';
  options?: GameOption[];
  dragDropConfig?: DragDropConfig;
  audioConfig?: AudioConfig;
  visualConfig?: VisualConfig;
  timeLimit?: number; // en segundos
  adaptiveHelp?: boolean;
  nextSceneId?: string;
}

export interface GameOption {
  id: string;
  text: string;
  icon?: string;
  score: number; // 0-100
  feedback?: string;
  nextSceneId?: string;
}

export interface DragDropConfig {
  items: DragDropItem[];
  targetZones: DragDropZone[];
  correctOrder?: string[];
}

export interface DragDropItem {
  id: string;
  text: string;
  icon?: string;
  category?: string;
}

export interface DragDropZone {
  id: string;
  title: string;
  accepts: string[];
}

export interface AudioConfig {
  audioUrl: string;
  transcript?: string;
  questions: AudioQuestion[];
}

export interface AudioQuestion {
  id: string;
  question: string;
  options: GameOption[];
}

export interface VisualConfig {
  imageUrl: string;
  interactiveAreas: InteractiveArea[];
  explorationMode?: boolean;
}

export interface InteractiveArea {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  action: 'click' | 'hover' | 'drag';
  feedback?: string;
}

export interface GameLog {
  sceneId: string;
  selectedOptionId?: string;
  timeSpent: number; // en milisegundos
  helpUsed: boolean;
  adaptations: string[];
  timestamp: Date;
}

export interface SoftSkill {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  gameId: string;
  level: 'bajo' | 'medio' | 'alto';
  score: number; // 0-100
  confidence: number; // 0-1
  logs: GameLog[];
}

export interface Game {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  softSkill: string;
  day: string;
  scenario: string;
  icon: string;
  color: string;
  scenes: GameScene[];
  completed: boolean;
  score?: number;
  logs: GameLog[];
}

export interface GameState {
  currentGameId?: string;
  currentSceneId?: string;
  completedGames: string[];
  gameLogs: Record<string, GameLog[]>;
  adaptations: string[];
  accessibility: AccessibilitySettings;
}

export interface AccessibilitySettings {
  contrastLevel: 'normal' | 'high';
  fontScale: number; // 80-150%
  audioEnabled: boolean;
  visualHelp: boolean;
  timeExtensions: boolean;
}

export interface EvaluationResult {
  userId: string;
  softSkills: SoftSkill[];
  employabilityScore: number;
  level: 'Baja empleabilidad' | 'Empleabilidad media' | 'Alta empleabilidad';
  cvAnalysis?: CVAnalysis;
  jobPreferences?: JobPreferences;
  reportGeneratedAt: Date;
}

export interface CVAnalysis {
  structure: 'bueno' | 'regular' | 'mejorable';
  coherence: 'bueno' | 'regular' | 'mejorable';
  experience: 'bueno' | 'regular' | 'mejorable';
  skills: string[];
  score: number; // 0-100
}

export interface JobPreferences {
  areas: string[];
  needs: string[];
  environment: string[];
  schedule: string[];
}

export interface GameProgress {
  totalGames: number;
  completedGames: number;
  currentGame?: string;
  overallScore?: number;
}