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
    
    // En lugar de devolver error, generar un informe básico
    try {
      const { preferences, minigames, cvAnalysis } = req.body;
      
      // Generar informe básico sin IA
      const informeBasico = generateBasicReport(preferences, minigames, cvAnalysis);
      
      return res.json({ informe: informeBasico });
    } catch (error) {
      return res.status(500).json({ 
        error: 'El servidor no está configurado correctamente para generar informes de IA.',
        details: 'Variables de entorno de Azure OpenAI no configuradas'
      });
    }
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
    console.log('cvAnalysis type:', typeof cvAnalysis);
    console.log('cvAnalysis keys:', cvAnalysis ? Object.keys(cvAnalysis) : 'null/undefined');

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

    // Construir prompt optimizado y conciso
    const prompt = `
Eres un orientador laboral experto. Genera un informe de empleabilidad PERSONALIZADO basado en los datos proporcionados.

**DATOS:**
- Preferencias: ${JSON.stringify(preferences, null, 2)}
- Minijuegos: ${JSON.stringify(minigames, null, 2)}
- CV: ${JSON.stringify(cvAnalysisToUse, null, 2)}

**ESTRUCTURA (Markdown, máximo 600 palabras):**

## 1. Análisis del CV
- Estructura: ${cvAnalysisToUse.structure}
- Coherencia: ${cvAnalysisToUse.coherence}
- Experiencia: ${cvAnalysisToUse.experience}
- Habilidades: ${cvAnalysisToUse.skills.length > 0 ? cvAnalysisToUse.skills.join(', ') : 'No detectadas'}
- Fortalezas: ${cvAnalysisToUse.strengths.join(', ') || 'No identificadas'}
- Mejoras: ${cvAnalysisToUse.weaknesses.join(', ') || 'No identificadas'}

## 2. Puntos Fuertes
Combina preferencias + minijuegos + CV para identificar 2-3 fortalezas únicas.

## 3. Áreas de Desarrollo
Para cada área de mejora, ofrece acciones específicas y recursos.

## 4. Recomendaciones Laborales
Sugiere roles específicos basados en preferencias Y experiencia del CV.

## 5. Próximos Pasos
Plan de 3 acciones concretas: esta semana, 1 mes, 3 meses.

**Reglas:** Sé específico, evita plantillas genéricas, cruza información de todas las fuentes.
`;

    // 2. Construcción correcta de la URL usando la variable de entorno
    const url = `${AZURE_OPENAI_ENDPOINT}openai/deployments/${AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version=${AZURE_OPENAI_API_VERSION}`;
    
    // Log de la URL y configuración para debug
    console.log('=== CONFIGURACIÓN AZURE OPENAI ===');
    console.log('URL:', url);
    console.log('Deployment:', AZURE_OPENAI_DEPLOYMENT);
    console.log('API Version:', AZURE_OPENAI_API_VERSION);
    console.log('API Key presente:', AZURE_OPENAI_API_KEY ? 'Sí' : 'No');
    console.log('Prompt length:', prompt.length, 'caracteres');
    
    // Llamada a Azure OpenAI optimizada
    console.log('Iniciando llamada a Azure OpenAI...');
    const startTime = Date.now();
    
    const response = await axios.post(
      url,
      {
        messages: [
          { role: 'system', content: 'Eres un orientador laboral experto. Genera informes concisos y específicos.' },
          { role: 'user', content: prompt }
        ],
        max_tokens: 800, // Reducido de 1500
        temperature: 0.5, // Reducido de 0.7 para respuestas más consistentes
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'api-key': AZURE_OPENAI_API_KEY,
        },
        timeout: 60000, // Timeout aumentado a 60 segundos
      }
    );
    
    const endTime = Date.now();
    console.log(`Azure OpenAI respondió en ${endTime - startTime}ms`);
    const informe = response.data.choices[0]?.message?.content || 'No se pudo generar el informe.';
    res.json({ informe });
  } catch (error: any) {
    // Log detallado del error de Azure/OpenAI o cualquier otro error
    console.error('=== ERROR DETALLADO ===');
    console.error('Error type:', error.constructor.name);
    console.error('Error code:', error.code);
    console.error('Error message:', error.message);
    console.error('Error response status:', error.response?.status);
    console.error('Error response data:', error.response?.data);
    console.error('Error stack:', error.stack);
    
    // Si es un error de timeout o conexión, generar informe básico
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout') || error.code === 'ENOTFOUND') {
      console.log('Error de timeout/conexión detectado, generando informe básico...');
      try {
        const { preferences, minigames, cvAnalysis } = req.body;
        const informeBasico = generateBasicReport(preferences, minigames, cvAnalysis);
        console.log('Informe básico generado exitosamente');
        return res.json({ informe: informeBasico });
      } catch (fallbackError) {
        console.error('Error generando informe básico:', fallbackError);
      }
    }
    
    // Si es un error de autenticación o configuración de Azure
    if (error.response?.status === 401) {
      console.error('Error de autenticación con Azure OpenAI - API Key inválida');
      return res.status(500).json({ error: 'Error de configuración: API Key de Azure OpenAI inválida' });
    }
    
    if (error.response?.status === 404) {
      console.error('Error 404 - Deployment no encontrado o URL incorrecta');
      return res.status(500).json({ error: 'Error de configuración: Deployment de Azure OpenAI no encontrado' });
    }
    
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

// Función para generar informe básico sin IA
function generateBasicReport(preferences: any, minigames: any[], cvAnalysis: any): string {
  const highSkills = minigames.filter(skill => skill.level === 'Alto');
  const mediumSkills = minigames.filter(skill => skill.level === 'Medio');
  const lowSkills = minigames.filter(skill => skill.level === 'Bajo');

  const totalScore = minigames.reduce((sum, skill) => sum + (skill.score || 0), 0) / Math.max(1, minigames.length);
  
  const level = totalScore >= 80 ? 'Alta empleabilidad' : totalScore >= 50 ? 'Empleabilidad media' : 'Baja empleabilidad';

  return `# Informe de Empleabilidad - Análisis Básico

## 1. Análisis del CV
- **Estructura:** ${cvAnalysis?.structure || 'Regular'}
- **Coherencia:** ${cvAnalysis?.coherence || 'Regular'}
- **Experiencia:** ${cvAnalysis?.experience || 'Regular'}
- **Habilidades detectadas:** ${cvAnalysis?.skills?.join(', ') || 'No detectadas'}
- **Fortalezas:** ${cvAnalysis?.strengths?.join(', ') || 'No identificadas'}
- **Áreas de mejora:** ${cvAnalysis?.weaknesses?.join(', ') || 'No identificadas'}

## 2. Puntos Fuertes
${highSkills.length > 0 ? `- **Habilidades destacadas:** ${highSkills.map(s => s.skill).join(', ')}` : '- Necesitas desarrollar más habilidades blandas'}
${preferences?.areas?.length > 0 ? `- **Áreas de interés:** ${preferences.areas.join(', ')}` : ''}

## 3. Áreas de Desarrollo
${lowSkills.length > 0 ? `- **Habilidades a mejorar:** ${lowSkills.map(s => s.skill).join(', ')}` : '- Todas las habilidades están en buen nivel'}
- **Recomendación:** Practica regularmente los minijuegos para mejorar tus habilidades

## 4. Recomendaciones Laborales
- **Nivel de empleabilidad:** ${level}
- **Roles sugeridos:** Desarrollador frontend, Soporte técnico, Analista de datos
- **Modo de trabajo preferido:** ${preferences?.workMode || 'No especificado'}

## 5. Próximos Pasos
1. **Esta semana:** Completa todos los minijuegos disponibles
2. **1 mes:** Actualiza tu CV con las mejoras sugeridas
3. **3 meses:** Busca oportunidades laborales en las áreas de tu interés

---
*Este es un informe básico generado automáticamente. Para un análisis más detallado, contacta con un orientador laboral.*`;
} 
