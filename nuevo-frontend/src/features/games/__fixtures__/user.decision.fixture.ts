// src/features/games/__fixtures__/user.decision.fixture.ts
import type { 
  GameLog 
} from '@/types/game'

export const gameLogFixture: GameLog = {
  sceneId: 'scene-1',
  selectedOptionId: 'opt-1',
  timeSpent: 5000,
  reactionTimeMs: 1200, // Añadido para el mock de telemetría
  helpUsed: false,
  adaptations: [],
  timestamp: new Date()
};