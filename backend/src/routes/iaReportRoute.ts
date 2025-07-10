import express from 'express';
import { Configuration, OpenAIApi } from 'openai';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
dotenv.config();

const router = express.Router();

const openai = new OpenAIApi(new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
}));

// POST /api/informe-ia
router.post('/', async (req, res) => {
  try {
    const { preferences, minigames, cvAnalysis } = req.body;

    // Construir prompt profesional
    const prompt = `Eres un orientador laboral experto. Genera un informe profesional, amable y personalizado para un candidato/a usando estos datos:

---
Preferencias laborales: ${JSON.stringify(preferences, null, 2)}
Resultados de minijuegos: ${JSON.stringify(minigames, null, 2)}
Análisis de CV: ${JSON.stringify(cvAnalysis, null, 2)}
---

El informe debe incluir:
1. Mapa de habilidades (resumen textual)
2. Fortalezas principales
3. Áreas de mejora y sugerencias prácticas
4. Recomendaciones laborales (puestos, sectores, entorno)
5. Análisis breve del CV
6. Próximos pasos sugeridos

Usa un tono motivador, claro y profesional. No repitas los datos en bruto, interpreta y personaliza el texto para la persona candidata.`;

    // Llamada a OpenAI
    const completion = await openai.createChatCompletion({
      model: 'gpt-3.5-turbo',
      messages: [
        { role: 'system', content: 'Eres un orientador laboral experto en empleabilidad.' },
        { role: 'user', content: prompt }
      ],
      max_tokens: 900,
      temperature: 0.7,
    });

    const informe = completion.data.choices[0]?.message?.content || 'No se pudo generar el informe.';
    res.json({ informe });
  } catch (error) {
    console.error('Error generando informe IA:', error);
    res.status(500).json({ error: 'Error generando informe IA' });
  }
});

// POST /api/ia-feedback
router.post('/feedback', async (req, res) => {
  try {
    const { informe, rating, comment, userData } = req.body;
    const feedback = {
      informe,
      rating,
      comment,
      userData,
      timestamp: new Date().toISOString(),
    };
    const feedbackPath = path.join(__dirname, '../../../feedback_ia.json');
    let feedbacks = [];
    if (fs.existsSync(feedbackPath)) {
      feedbacks = JSON.parse(fs.readFileSync(feedbackPath, 'utf8'));
    }
    feedbacks.push(feedback);
    fs.writeFileSync(feedbackPath, JSON.stringify(feedbacks, null, 2));
    res.json({ ok: true });
  } catch (error) {
    res.status(500).json({ error: 'Error guardando feedback IA' });
  }
});

export default router; 