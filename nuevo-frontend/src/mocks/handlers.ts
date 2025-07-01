// src/mocks/handlers.ts

import { rest } from 'msw'
import type { RestRequest, ResponseResolver, RestContext } from 'msw'

export const handlers = [
  // Minijuego 1 - Toma de decisiones
  rest.get('/api/scenes/1.json', (req: RestRequest, res: any, ctx: RestContext) => {
    return res(
      ctx.status(200),
      ctx.json({
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
        ]
      })
    )
  }),

  // Minijuego 2 - Resolución de problemas
  rest.get('/api/scenes/2.json', (req: RestRequest, res: any, ctx: RestContext) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: 2,
        title: 'Minijuego 2: Algo no cuadra',
        steps: [
          {
            text: 'Recibes un pedido incompleto. Debes decidir cómo actuar.',
            options: [
              {
                text: 'Anotas el error y lo reportas.',
                isCorrect: true,
                skillImpact: { 'Resolución de problemas': 0.9 },
                feedback: 'Buena resolución de problemas. Has actuado con precisión.'
              },
              {
                text: 'Tomas la iniciativa de ir a buscar lo que falta.',
                isCorrect: false,
                skillImpact: { 'Resolución de problemas': 0.6 },
                feedback: 'Puedes mejorar en seguir procesos establecidos.'
              }
            ]
          }
        ]
      })
    )
  }),

  // Minijuego 3 - Trabajo en equipo
  rest.get('/api/scenes/3.json', (req: RestRequest, res: any, ctx: RestContext) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: 3,
        title: 'Minijuego 3: El envío urgente',
        steps: [
          {
            text: 'Formas parte de un equipo encargado de preparar un envío crítico.',
            options: [
              {
                text: 'Asignas tareas según habilidades de cada uno.',
                isCorrect: true,
                skillImpact: { 'Trabajo en equipo': 0.9 },
                feedback: 'Gran trabajo en equipo. Distribuiste tareas de forma efectiva.'
              },
              {
                text: 'Haces todo tú mism@ para que salga bien.',
                isCorrect: false,
                skillImpact: { 'Trabajo en equipo': 0.4 },
                feedback: 'Demasiado control. Es importante confiar en el equipo.'
              }
            ]
          }
        ]
      })
    )
  }),

  // Minijuego 5 - Comunicación
  rest.get('/api/scenes/5.json', (req: RestRequest, res: any, ctx: RestContext) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: 5,
        title: 'Minijuego 5: Reunión sorpresa',
        steps: [
          {
            text: 'Te toca hablar en la reunión. ¿Cómo lo haces?',
            options: [
              {
                text: 'Explicas claro y escuchas activamente',
                isCorrect: true,
                skillImpact: { 'Comunicación': 0.9 },
                feedback: 'Muy buena comunicación. Claro y empático.'
              },
              {
                text: 'Prefieres no participar mucho.',
                isCorrect: false,
                skillImpact: { 'Comunicación': 0.4 },
                feedback: 'Falta de participación puede interpretarse como desinterés.'
              }
            ]
          }
        ]
      })
    )
  }),

  // Logs
  rest.post('/api/logs/step', (req: RestRequest, res: any, ctx: RestContext) => {
    return res(ctx.status(200))
  }),

  rest.post('/api/logs/game-complete', (req: RestRequest, res: any, ctx: RestContext) => {
    return res(ctx.status(200), ctx.json({ success: true }))
  })
]