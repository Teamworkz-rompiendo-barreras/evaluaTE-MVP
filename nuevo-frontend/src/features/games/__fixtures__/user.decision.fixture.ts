// src/features/games/__fixtures__/user.decision.fixture.ts
import type { 
  GameLog 
} from '@/types/game'

export const gameLogFixture: GameLog = {
  sceneId: 'test-scene-1',
  selectedOptionId: 'option-1',
  timeSpent: 5000,
  helpUsed: false,
  adaptations: [],
  timestamp: new Date()
}