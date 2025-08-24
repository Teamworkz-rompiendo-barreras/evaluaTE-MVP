// src/features/games/__fixtures__/scene.fixture.ts
import type { GameScene } from '@/types/game'

export const sceneFixture: GameScene = {
  id: 'test-scene-1',
  title: 'Escena de prueba',
  description: 'Esta es una escena de prueba para testing',
  type: 'choice',
  options: [
    {
      id: 'option-1',
      text: 'Opción 1',
      score: 100
    },
    {
      id: 'option-2',
      text: 'Opción 2',
      score: 50
    }
  ],
  nextSceneId: 'test-scene-2'
}