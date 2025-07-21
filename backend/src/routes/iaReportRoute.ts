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
    return res.status(500).json({ error: 'El servidor no está configurado correctamente para generar informes de IA.' });
  }

  try {
    const { preferences, minigames, cvAnalysis } = req.body;

    // Construir prompt profesional y detallado
    const prompt = `
Eres un experto en orientación laboral y análisis de talento, con un enfoque humano, motivador y profesional. Tu objetivo es generar un informe de empleabilidad excepcional, personalizado y accionable para un candidato/a.

**Contexto del candidato/a:**
*   **Preferencias laborales:** ${JSON.stringify(preferences, null, 2)}
*   **Resultados de minijuegos (habilidades):** ${JSON.stringify(minigames, null, 2)}
*   **Análisis preliminar del CV:** ${JSON.stringify(cvAnalysis, null, 2)}

---

**Feedback de un usuario anterior (esto es lo que DEBES EVITAR):**
"En áreas de mejora me vuelve a poner lo mismo que en el resumen del radar chart, no me aporta nada nuevo. Y las sugerencias son todo el rato lo mismo. Las recomendaciones laborales son absurdas ('Completar todos los juegos'). El análisis del CV es vago ('estructura regular'). Los próximos pasos son genéricos ('actualiza tu CV')."

---

**INSTRUCCIONES PARA EL INFORME (usa formato Markdown):**

**1. Análisis de tu CV:**
   - **Estructura y Coherencia:** Evalúa si el CV es claro, profesional y fácil de leer. Ofrece sugerencias específicas. Por ejemplo, en lugar de decir "estructura regular", di "Tu CV tiene una base sólida, pero podrías mejorar la sección de experiencia utilizando verbos de acción más potentes. Por ejemplo, en lugar de 'responsable de tareas', prueba con 'lideré la implementación de...'".
   - **Habilidades Detectadas:** Extrae y lista las habilidades clave (técnicas y blandas) que identificas en el CV. Si no detectas ninguna, explícalo de forma constructiva.

**2. Tus Puntos Fuertes:**
   - **NO** te limites a listar las puntuaciones altas de los minijuegos.
   - **SÍ** cruza la información del CV (experiencia, logros), las preferencias (sectores de interés) y los minijuegos para identificar 2-3 fortalezas clave.
   - **Ejemplo:** "Tu habilidad en 'Resolución de Problemas' (resultado del minijuego) se refleja claramente en tu experiencia en el proyecto X (del CV), donde lideraste la solución a un problema complejo. Esta es una fortaleza muy demandada en el sector de la consultoría (tu preferencia)."

**3. Áreas de Desarrollo y Sugerencias Prácticas:**
   - **NO** repitas simplemente los resultados de los minijuegos con puntuaciones bajas.
   - **SÍ** identifica 2-3 áreas de mejora realistas. Para cada una, ofrece sugerencias concretas y accionables.
   - **Ejemplo:** "Para potenciar tu 'Comunicación Asertiva', te sugiero practicar con el método 'STAR' (Situación, Tarea, Acción, Resultado) al describir tus logros en entrevistas. También puedes unirte a un club de debate como Toastmasters."

**4. Recomendaciones Laborales:**
   - Basándote en **TODOS** los datos, sugiere 2-3 roles o puestos de trabajo específicos.
   - Menciona sectores y tipos de empresa (startup, corporación, ONG) donde el perfil del candidato/a podría encajar bien.
   - **Ejemplo:** "Dado tu interés en el sector tecnológico y tus habilidades analíticas, podrías explorar roles como 'Analista de Datos Junior' o 'Business Intelligence Analyst' en startups de crecimiento."

**5. Próximos Pasos para tu Carrera:**
   - Ofrece un plan de acción con 3-4 pasos claros y orientados a la búsqueda de empleo y desarrollo profesional.
   - **Ejemplos de pasos útiles:** "1. Adapta tu CV para la oferta X, destacando tus logros en Y. 2. Prepara una entrevista para un rol de 'Project Manager' investigando sobre la empresa Z. 3. Considera realizar el curso online de 'Gestión de Proyectos Ágil con Scrum' [enlace al curso] para fortalecer tu perfil."

**Formato Final:**
- Usa Markdown (## para títulos, * para listas).
- Tono profesional, cercano y siempre constructivo.
- El informe debe ser 100% original y basado en los datos proporcionados. ¡No uses plantillas!
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
        max_tokens: 900,
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
    console.error('Error generando informe IA:', error?.response?.data || error.message || error);
    res.status(500).json({ error: 'Error generando informe IA' });
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
