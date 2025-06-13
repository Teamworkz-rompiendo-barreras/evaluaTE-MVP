// backend/generate-report.test.ts
import { describe, it, expect, afterAll } from 'vitest'
import request from 'supertest'
import server from './index'  // Importa el servidor Express para Supertest

describe('POST /api/generate-report', () => {
  it('debe devolver un PDF válido', async () => {
    const res = await request(server)
      .post('/api/generate-report')
      .send({
        gameData: [{ subject: 'Minijuego 0', dA: 100 }],
        cvAnalysis: { score: 90, strengths: ['X'], weaknesses: ['Y'] },
      })
      .expect(200)
      .expect('Content-Type', /application\/pdf/)

    expect(res.body.length).toBeGreaterThan(1000)
  })
})

// Cierra el servidor tras los tests para evitar open handles
afterAll(async () => {
  await server.close()
})
