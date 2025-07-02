// backend/tests/generate-report.test.ts
import request from 'supertest';
import { app, server } from '../src/app'; // Asegúrate de que la ruta sea correcta

describe('POST /api/generate-report', () => {
  beforeAll((done) => {
    server.listen(3001, done);
  });

  afterAll((done) => {
    server.close(done);
  });

  it('debe devolver un PDF válido', async () => {
    const res = await request(server)
      .post('/api/generate-report')
      .send({
        gameData: [{ subject: 'Minijuego 0', dA: 100 }],
        cvAnalysis: {
          structure: 'bueno',
          coherence: 'bueno',
          experience: 'bueno',
          skills: ['habilidad1', 'habilidad2'],
        },
        jobPreferences: {
          areas: ['Logística', 'Atención al cliente'],
          needs: ['Trabajo en entorno tranquilo'],
        },
      });

    expect(res.status).toBe(200);
    expect(res.headers['content-type']).toBe('application/pdf');
    expect(res.body).toBeInstanceOf(Buffer);
  });
});