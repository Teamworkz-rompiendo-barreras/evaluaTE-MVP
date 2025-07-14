// src/features/games/__fixtures__/scene.fixture.ts
import type { GameScene } from '@/types/game-scene'

export const mockScene1: GameScene = {
  id: 1,
  title: 'Minijuego 1: La primera llamada',
  steps: [
    {
      text: 'Recibes una llamada inesperada. ¿Qué haces?',
      options: [
        {
          text: 'Respondes de inmediato',
          isCorrect: true,
          skillImpact: { 'Toma de decisiones': 0.9 },
          feedback: 'Buena toma de decisión. Has actuado con responsabilidad.'
        },
        {
          text: 'Pides tiempo para pensar',
          isCorrect: false,
          skillImpact: { 'Toma de decisiones': 0.5 },
          feedback: 'Has querido ayudar, pero es mejor asegurarse antes de actuar.'
        }
      ]
    }
  ],
  softSkillsTracked: ['Toma de decisiones'],
  accessibilityOptions: {
    showPictograms: true,
    audioAssistiveMode: true,
    contrastLevel: 'normal'
  }
}

export const mockScene3: GameScene = {
  id: 3,
  title: 'Minijuego 3: Sistema caído',
  steps: [
    {
      text: 'El sistema se ha caído durante tu jornada laboral.',
      options: [
        {
          text: 'Preguntas si hay forma alternativa de hacerlo en papel',
          isCorrect: true,
          skillImpact: { 'Flexibilidad operativa': 0.8 },
          feedback: 'Buena adaptación. Encontraste una solución alternativa.'
        },
        {
          text: 'Esperas sin hacer nada',
          isCorrect: false,
          skillImpact: { 'Autonomía': 0.4 },
          feedback: 'Demasiada dependencia de la tecnología.'
        }
      ]
    }
  ],
  softSkillsTracked: ['Flexibilidad operativa', 'Autonomía'],
  accessibilityOptions: {
    showPictograms: true,
    audioAssistiveMode: false,
    contrastLevel: 'alto'
  }
}