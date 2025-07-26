import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import cors from 'cors';
import axios from 'axios';
dotenv.config();

const router = express.Router();

// Aplica cors solo a este router, por si el global no lo detecta
router.use(cors({
  origin: [
    'http://localhost:3005',
    'http://localhost:5173',
    'https://yellow-mud-0b6281c1e.6.azurestaticapps.net',
    'https://*.azurestaticapps.net',
    'https://*.azurewebsites.net'
  ],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Origin', 'Accept'],
  credentials: true,
  optionsSuccessStatus: 200,
  preflightContinue: false
}))

// Responde a preflight OPTIONS
router.options('*', cors());

// Variables de entorno para Azure OpenAI
const AZURE_OPENAI_API_KEY = process.env.AZURE_OPENAI_API_KEY;
const AZURE_OPENAI_ENDPOINT = process.env.AZURE_OPENAI_ENDPOINT;
const AZURE_OPENAI_DEPLOYMENT = process.env.AZURE_OPENAI_DEPLOYMENT;
const AZURE_OPENAI_API_VERSION = process.env.AZURE_OPENAI_API_VERSION;

// POST /api/informe-ia
router.post('/', async (req: Request, res: Response) => {
  // 1. Validación rigurosa de las variables de entorno
  if (!AZURE_OPENAI_API_KEY || !AZURE_OPENAI_ENDPOINT || !AZURE_OPENAI_DEPLOYMENT || !AZURE_OPENAI_API_VERSION) {
    console.error('Error: Faltan variables de entorno para el servicio de Azure OpenAI.');
    console.error('AZURE_OPENAI_API_KEY:', AZURE_OPENAI_API_KEY ? 'Presente' : 'Faltante');
    console.error('AZURE_OPENAI_ENDPOINT:', AZURE_OPENAI_ENDPOINT ? 'Presente' : 'Faltante');
    console.error('AZURE_OPENAI_DEPLOYMENT:', AZURE_OPENAI_DEPLOYMENT ? 'Presente' : 'Faltante');
    console.error('AZURE_OPENAI_API_VERSION:', AZURE_OPENAI_API_VERSION ? 'Presente' : 'Faltante');
    return res.status(500).json({ error: 'El servidor no está configurado correctamente para generar informes de IA.' });
  }

  // Log del payload recibido
  console.log('Payload recibido en /api/informe-ia:', JSON.stringify(req.body, null, 2));

  try {
    const { preferences, minigames, cvAnalysis } = req.body;
    
    // Log completo del body para debug
    console.log('Body completo recibido:', JSON.stringify(req.body, null, 2));
    console.log('preferences:', preferences);
    console.log('minigames:', minigames);
    console.log('cvAnalysis:', cvAnalysis);

    // Validación de datos de entrada
    if (!preferences || !minigames) {
      console.error('Error: Faltan datos requeridos (preferences o minigames)');
      return res.status(400).json({ error: 'Faltan datos requeridos para generar el informe.' });
    }

    // Validación del análisis de CV - más permisiva
    if (!cvAnalysis) {
      console.error('Error: No se proporcionó análisis de CV.');
      return res.status(400).json({ error: 'No se ha podido analizar el CV. Por favor, revisa el archivo enviado o inténtalo de nuevo.' });
    }

    // Si el CV no se pudo analizar completamente, crear un análisis básico
    const cvAnalysisToUse = {
      structure: cvAnalysis.structure || 'regular',
      coherence: cvAnalysis.coherence || 'regular',
      experience: cvAnalysis.experience || 'regular',
      skills: cvAnalysis.skills || [],
      strengths: cvAnalysis.strengths || [],
      weaknesses: cvAnalysis.weaknesses || [],
      feedback: cvAnalysis.feedback && cvAnalysis.feedback.trim() !== '' ? cvAnalysis.feedback : 'No se pudo analizar completamente el CV',
      alerts: cvAnalysis.alerts || ['Análisis limitado del CV']
    };

    // Log para debug
    console.log('cvAnalysis recibido:', JSON.stringify(cvAnalysis, null, 2));
    console.log('cvAnalysisToUse procesado:', JSON.stringify(cvAnalysisToUse, null, 2));

    // Construir prompt profesional y detallado
    const prompt = `
Eres un experto en orientación laboral y análisis de talento. Genera un informe de empleabilidad PERSONALIZADO y ACCIONABLE basado ÚNICAMENTE en los datos proporcionados.

**DATOS DEL CANDIDATO/A:**
*   **Preferencias laborales:** ${JSON.stringify(preferences, null, 2)}
*   **Resultados de minijuegos:** ${JSON.stringify(minigames, null, 2)}
*   **Análisis del CV:** ${JSON.stringify(cvAnalysisToUse, null, 2)}

**REGLAS IMPORTANTES:**
1. **NO uses plantillas genéricas** - cada recomendación debe basarse en los datos específicos
2. **Si el CV no se pudo analizar**, enfócate en los minijuegos y preferencias
3. **NO repitas información** - no digas "tienes X en toma de decisiones" si ya está en el radar
4. **Sé específico** - evita consejos genéricos como "mejora tu CV"

---

**ESTRUCTURA DEL INFORME (Markdown):**

## 1. Análisis de tu CV
**Estructura y Coherencia:** 
- Si el CV se analizó: Evalúa la estructura real y ofrece sugerencias específicas
- Si no se pudo analizar: Explica por qué y qué hacer al respecto

**Habilidades Detectadas:**
- Lista las habilidades técnicas y blandas encontradas en el CV
- Si no hay habilidades detectadas, explica constructivamente por qué

## 2. Tus Puntos Fuertes
**Cruza información de múltiples fuentes:**
- Combina preferencias laborales + resultados de minijuegos + experiencia del CV
- Identifica 2-3 fortalezas únicas y específicas
- **Ejemplo:** "Tu interés en roles prácticos (jardinero, barista) se alinea perfectamente con tu alta puntuación en 'Curiosidad y aprendizaje' (50%). Esto sugiere que te adaptas bien a nuevos entornos y aprendes rápidamente."

## 3. Áreas de Desarrollo y Sugerencias Prácticas
**Para cada área de mejora, ofrece:**
- **Por qué es importante** para sus preferencias laborales
- **Cómo mejorar** con acciones específicas y medibles
- **Recursos concretos** (cursos, prácticas, etc.)

**Ejemplo:** "**Influencia Social (17%):** Aunque prefieres roles prácticos, la interacción con clientes es inevitable. **Mejora:** Practica técnicas de venta en tu trabajo actual, toma un curso de atención al cliente en Coursera."

## 4. Recomendaciones Laborales Específicas
**Basándote en sus preferencias reales:**
- Sugiere roles específicos en sus áreas de interés
- Menciona tipos de empresas donde encajarían
- Considera su disponibilidad (remoto, completa)

## 5. Próximos Pasos Accionables
**Plan de 3-4 pasos específicos:**
1. Acción concreta para esta semana
2. Objetivo a corto plazo (1 mes)
3. Desarrollo a medio plazo (3 meses)
4. Recursos específicos (cursos, plataformas, etc.)

**Formato:** Usa Markdown con ## para títulos principales y ### para subtítulos. Tono profesional pero cercano. Máximo 800 palabras.
`;

    // 2. Construcción correcta de la URL usando la variable de entorno
    const url = `${AZURE_OPENAI_ENDPOINT}openai/deployments/${AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version=${AZURE_OPENAI_API_VERSION}`;
    
    // Llamada a Azure OpenAI
    const response = await axios.post(
      url,
      {
        messages: [
          { role: 'system', content: 'Eres un orientador laboral experto en empleabilidad.' },
          { role: 'user', content: prompt }
        ],
        max_tokens: 1500,
        temperature: 0.7,
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'api-key': AZURE_OPENAI_API_KEY,
        },
      }
    );
    const informe = response.data.choices[0]?.message?.content || 'No se pudo generar el informe.';
    res.json({ informe });
  } catch (error: any) {
    // Log detallado del error de Azure/OpenAI o cualquier otro error
    console.error('Error en /api/informe-ia:', error?.response?.data || error.message || error);
    res.status(500).json({ error: 'Error generando informe IA: ' + (error?.response?.data?.error?.message || error.message || 'Error desconocido') });
  }
});

// POST /api/ia-feedback
router.post('/feedback', async (req: Request, res: Response) => {
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
