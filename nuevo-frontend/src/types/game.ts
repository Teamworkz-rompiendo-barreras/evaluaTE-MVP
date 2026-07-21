// nuevo-frontend/src/types/game.ts

export interface GameOption {
  id: string;
  text: string;
  icon?: string; 
  score: number;
  feedback?: string;      
  nextSceneId?: string;   
}

// ==========================================
// INTERFACES PARA ESCENAS MULTIMODALES
// ==========================================

export interface DragDropItem {
  id: string;
  content?: string;
  imageUrl?: string;
  icon?: string; 
  text?: string; 
}

export interface DragDropZone {
  id: string;
  title?: string;
  acceptedItemIds?: string[];
}

export interface DragDropConfig {
  items: DragDropItem[];
  targetZones: DragDropZone[];
  correctOrder?: string[]; 
}

export interface InteractiveArea {
  id: string;
  feedback?: string;
  x?: number; 
  y?: number;
  width?: number;  
  height?: number; 
}

export interface VisualConfig {
  imageUrl?: string;
  interactiveAreas: InteractiveArea[];
  explorationMode?: boolean; 
}

export interface AudioQuestion {
  id: string;
  question?: string; 
  text?: string;
  options: GameOption[];
}

export interface AudioConfig {
  audioUrl?: string;
  transcript?: string; 
  questions: AudioQuestion[];
}

// ==========================================
// MODELO CENTRAL AMPLIADO
// ==========================================

export interface GameScene {
  id: string;
  title: string;
  description: string;
  type: 'choice' | 'info' | 'drag-drop' | 'audio' | 'visual-exploration';
  options?: GameOption[];
  nextSceneId?: string;
  
  // Atributos de gamificación y accesibilidad
  adaptiveHelp?: string | boolean; 
  timeLimit?: number; 

  // Configuraciones específicas por tipo de escena
  dragDropConfig?: DragDropConfig;
  visualConfig?: VisualConfig;
  audioConfig?: AudioConfig;
}

export interface GameLog {
  sceneId: string;
  selectedOptionId?: string; 
  reactionTimeMs: number;
  timeSpent?: number; 
  helpUsed?: boolean; 
  adaptations?: string[]; // <-- AÑADE ESTA ÚLTIMA LÍNEA
  timestamp: string | Date; 
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
  completed: boolean;
  logs: GameLog[];
  scenes: GameScene[];
}

export interface SoftSkill {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  gameId: string;
  level: 'bajo' | 'medio' | 'alto';
  score: number;
  confidence: number;
  logs: GameLog[];
}

export interface GameProgress {
  totalGames: number;
  completedGames: number;
  currentGame?: string;
}