import { describe, it, expect } from 'vitest'
import request from 'supertest'
import app from './index'

describe('POST /api/generate-report', () => {
  it('debe devolver un PDF válido', async () => {
    const res = await request(app)
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
