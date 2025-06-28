// src/mocks/handlers.ts
import { rest } from 'msw'

export const handlers = [
  rest.get('/api/scenes/1.json', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: 1,
        title: 'Minijuego 1: Primera llamada del día',
        steps: [
          {
            text: 'Recibes una llamada inesperada. ¿Qué haces?',
            options: [
              { text: 'Respondes de inmediato', isCorrect: true },
              { text: 'Pides tiempo para pensar', isCorrect: false }
            ]
          }
        ]
      })
    )
  }),

  rest.post('/api/logs/step', (req, res, ctx) => {
    return res(ctx.status(200))
  }),

  rest.post('/api/logs/game-complete', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({ success: true }))
  })
]