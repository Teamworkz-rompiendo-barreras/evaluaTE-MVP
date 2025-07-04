// backend/tests/generate-report.test.ts
import request from 'supertest';
import { app } from '../src/app'; // Asegúrate de que la ruta sea correcta
import { describe, it, expect, beforeAll, afterAll } from 'vitest';

let server: any;
let baseURL: string;

describe('POST /api/generate-report', () => {
  beforeAll(async () => {
    // Usar puerto aleatorio para evitar conflictos
    server = app.listen(0);
    const address = server.address();
    const port = typeof address === 'string' ? 3001 : address.port;
    baseURL = `http://localhost:${port}`;
  });

  afterAll(async () => {
    await new Promise<void>((resolve, reject) => {
      server.close((err: any) => (err ? reject(err) : resolve()));
    });
  });

  it('debe devolver un PDF válido', async () => {
    const res = await request(baseURL)
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
        employabilityScore: 75,
        level: 'Empleabilidad media',
        adjustedScore: 70,
        completedGames: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      })
      .timeout({ response: 5000, deadline: 10000 });

    expect(res.status).toBe(200);
    expect(res.headers['content-type']).toBe('application/pdf');
    expect(res.body).toBeInstanceOf(Buffer);
  });

  it('debe manejar solicitudes con datos incompletos', async () => {
    const res = await request(baseURL)
      .post('/api/generate-report')
      .send({
        gameData: [{ subject: 'Minijuego 0', dA: 100 }],
        cvAnalysis: {
          structure: 'bueno',
          coherence: 'bueno',
          experience: 'bueno',
          skills: ['habilidad1', 'habilidad2'],
        },
        // jobPreferences no está incluido para simular datos incompletos
      })
      .timeout({ response: 5000, deadline: 10000 });

    expect(res.status).toBe(400);
    expect(res.headers['content-type']).toBe('application/json');
    expect(res.body.error).toContain('Datos inválidos');
    expect(res.body.error).toContain('jobPreferences es requerido');
  });

  it('debe manejar solicitudes con datos inválidos', async () => {
    const res = await request(baseURL)
      .post('/api/generate-report')
      .send({
        gameData: 'invalid data', // Datos inválidos
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
      })
      .timeout({ response: 5000, deadline: 10000 });

    expect(res.status).toBe(400);
    expect(res.headers['content-type']).toBe('application/json');
    expect(res.body.error).toContain('Datos inválidos');
    expect(res.body.error).toContain('gameData debe ser un array');
  });
});