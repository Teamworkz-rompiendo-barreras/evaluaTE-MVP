// src/features/games/__fixtures__/user.decision.fixture.ts

import type {
  UserDecision
} from '@/types/game-scene'

export const userDecision1: UserDecision = {
  sceneId: 1,
  stepIndex: 0,
  optionText: 'Respondes de inmediato',
  isCorrect: true,
  skillImpacts: { 'Toma de decisiones': 0.9 },
  timestamp: new Date().toISOString(),
  userAgent: 'test-agent',
  screenResolution: '1920x1080',
}

export const userDecision2: UserDecision = {
  sceneId: 1,
  stepIndex: 1,
  optionText: 'Organizas según prioridad',
  isCorrect: true,
  skillImpacts: { 'Resolución de problemas': 0.8 },
  timestamp: new Date().toISOString(),
  userAgent: 'test-agent',
  screenResolution: '1920x1080',
}

export const userDecision3: UserDecision = {
  sceneId: 3,
  stepIndex: 0,
  optionText: 'Llamas a soporte técnico',
  isCorrect: false,
  skillImpacts: { 'Autonomía': 0.4 },
  timestamp: new Date().toISOString(),
  userAgent: 'test-agent',
  screenResolution: '1920x1080',
}

export const userDecision4: UserDecision = {
  sceneId: 3,
  stepIndex: 1,
  optionText: 'Reinicias el equipo',
  isCorrect: true,
  skillImpacts: { 'Gestión del tiempo': 0.75 },
  timestamp: new Date().toISOString(),
  userAgent: 'test-agent',
  screenResolution: '1920x1080',
}

export const userDecisionsForScene1 = [
  userDecision1,
  userDecision2,
]

export const userDecisionsForScene3 = [
  userDecision3,
  userDecision4,
]