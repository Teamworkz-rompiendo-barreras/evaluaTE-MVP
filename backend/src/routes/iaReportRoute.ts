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
      education: cvAnalysis.education || [],
      feedback: cvAnalysis.feedback && cvAnalysis.feedback.trim() !== '' ? cvAnalysis.feedback : 'No se pudo analizar completamente el CV',
      alerts: cvAnalysis.alerts || ['Análisis limitado del CV']
    };

    // Log para debug
    console.log('cvAnalysis recibido:', JSON.stringify(cvAnalysis, null, 2));
    console.log('cvAnalysisToUse procesado:', JSON.stringify(cvAnalysisToUse, null, 2));

    // Preparar el perfil completo para el análisis profesional de IA
    const perfil_completo = {
      datos_personales: {
        nombre: preferences.fullName || 'Usuario',
        user_id: preferences.userId || 'user123'
      },
      habilidades_soft: minigames.map((game: any) => ({
        habilidad: game.skill || game.name || 'Habilidad',
        puntuacion: game.score || game.value || 0,
        nivel: game.level || (game.score >= 70 ? 'Alto' : game.score >= 40 ? 'Medio' : 'Bajo'),
        confianza: game.confidence || 80
      })),
      analisis_cv: cvAnalysisToUse,
      preferencias_laborales: preferences,
      juegos_completados: minigames.map((game: any) => game.name || game.skill || 'Juego'),
      logs_juegos: []
    };
    
    // Convertir a formato de texto para la IA
    const perfil_texto = `
PERFIL COMPLETO DEL CANDIDATO:

DATOS PERSONALES:
- Nombre: ${perfil_completo.datos_personales.nombre}
- ID: ${perfil_completo.datos_personales.user_id}

HABILIDADES SOFT EVALUADAS:
${perfil_completo.habilidades_soft.map((h: any) => `- ${h.habilidad}: ${h.puntuacion}% (Nivel: ${h.nivel}, Confianza: ${h.confianza}%)`).join('\n')}

ANÁLISIS DEL CV:
${JSON.stringify(perfil_completo.analisis_cv, null, 2)}

PREFERENCIAS LABORALES:
${JSON.stringify(perfil_completo.preferencias_laborales, null, 2)}

JUEGOS COMPLETADOS:
${perfil_completo.juegos_completados.join(', ')}

LOGS DE JUEGOS:
${JSON.stringify(perfil_completo.logs_juegos, null, 2)}
`;

    console.log('🤖 Generando informe profesional con IA...');
    
    try {
      // Generar informe profesional usando Azure OpenAI
      const informe_profesional = await generarInformeProfesional(perfil_texto);
      console.log('✅ Informe profesional generado exitosamente');
      
      res.json({ informe: informe_profesional });
    } catch (iaError) {
      console.error('❌ Error generando informe profesional:', iaError);
      
      // Fallback: generar informe básico
      console.log('🔄 Generando informe básico como fallback...');
      const informeBasico = generateBasicReport(preferences, minigames, cvAnalysisToUse);
      res.json({ informe: informeBasico });
    }
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

// Función para generar informe profesional usando Azure OpenAI
async function generarInformeProfesional(perfil: string): Promise<string> {
  const url = `${AZURE_OPENAI_ENDPOINT}openai/deployments/${AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version=${AZURE_OPENAI_API_VERSION}`;
  
  const prompt = `
Eres un orientador laboral experto en neuroinclusión, con formación en psicología y especialización en empleabilidad para personas neurodivergentes. Tu misión es realizar un análisis integral y profesional del candidato, considerando todos los aspectos evaluados.

---

DATOS DEL CANDIDATO A ANALIZAR:
${perfil}

---

INSTRUCCIONES PARA EL ANÁLISIS:

1. **ANÁLISIS INTEGRAL**: Debes analizar en conjunto:
   - Preferencias laborales y motivaciones
   - Resultados de los minijuegos (habilidades cognitivas y soft skills)
   - Experiencia y formación del CV
   - Factores de neuroinclusión y accesibilidad

2. **PERSPECTIVA PROFESIONAL**: Redacta como un psicólogo laboral experto que:
   - Comprende las fortalezas neurodivergentes
   - Identifica barreras y facilitadores laborales
   - Propone adaptaciones y estrategias de inclusión
   - Utiliza evidencia científica en sus recomendaciones

3. **ENFOQUE NEUROINCLUSIVO**: Considera:
   - Fortalezas cognitivas únicas
   - Estilos de aprendizaje y comunicación
   - Necesidades de adaptación en el entorno laboral
   - Potencial de desarrollo y crecimiento

---

ESTRUCTURA DEL INFORME PROFESIONAL:

## 1. RESUMEN EJECUTIVO
(2-3 párrafos que sinteticen el perfil completo del candidato, destacando sus características principales, experiencia relevante y potencial laboral desde una perspectiva neuroinclusiva)

## 2. ANÁLISIS DE COMPETENCIAS COGNITIVAS Y SOFT SKILLS
### 2.1 Fortalezas Identificadas
- Análisis detallado de las habilidades cognitivas evaluadas
- Interpretación de los resultados de los minijuegos
- Relación con competencias laborales específicas

### 2.2 Áreas de Desarrollo
- Identificación de oportunidades de mejora
- Estrategias de compensación y adaptación
- Recursos y herramientas de apoyo

## 3. ANÁLISIS DE PREFERENCIAS Y MOTIVACIONES LABORALES
### 3.1 Perfil Motivacional
- Análisis de las preferencias expresadas
- Compatibilidad con diferentes entornos laborales
- Factores de satisfacción y retención

### 3.2 Estilo de Trabajo Preferido
- Condiciones laborales ideales
- Tipo de supervisión y comunicación preferida
- Entorno físico y social óptimo

## 4. EVALUACIÓN DE EXPERIENCIA Y FORMACIÓN
### 4.1 Análisis del CV
- Revisión de experiencia laboral previa
- Formación académica y profesional
- Transferibilidad de competencias

### 4.2 Brechas y Oportunidades
- Identificación de necesidades formativas
- Experiencia complementaria recomendada
- Certificaciones o formación adicional sugerida

## 5. RECOMENDACIONES DE EMPLEABILIDAD NEUROINCLUSIVA
### 5.1 Puestos de Trabajo Recomendados
- 3-4 propuestas específicas con justificación
- Análisis de compatibilidad con el perfil
- Perspectivas de desarrollo en cada rol

### 5.2 Adaptaciones y Acompañamiento Recomendado
- Ajustes en el entorno laboral
- Estrategias de comunicación y supervisión
- Recursos de apoyo y desarrollo

### 5.3 Plan de Desarrollo Profesional
- Objetivos a corto, medio y largo plazo
- Recursos y herramientas recomendadas
- Seguimiento y evaluación del progreso

## 6. CONCLUSIONES Y PRÓXIMOS PASOS
- Síntesis de las principales recomendaciones
- Acciones inmediatas recomendadas
- Expectativas realistas de empleabilidad

---

CRITERIOS DE CALIDAD:
- Lenguaje profesional pero accesible
- Análisis basado en evidencia y experiencia clínica
- Recomendaciones prácticas y realizables
- Enfoque positivo y empoderador
- Consideración integral de factores neuroinclusivos
- Propuestas específicas y contextualizadas
`;

  const response = await axios.post(
    url,
    {
      messages: [
        { 
          role: 'system', 
          content: 'Eres un psicólogo laboral experto en neuroinclusión, con más de 15 años de experiencia en orientación profesional para personas neurodivergentes. Tienes formación en psicología clínica, neuropsicología y empleabilidad. Tu enfoque es científico, empático y basado en evidencia. Siempre consideras las fortalezas únicas de cada persona y propones adaptaciones prácticas para maximizar su potencial laboral.' 
        },
        { role: 'user', content: prompt }
      ],
      max_tokens: 4000,
      temperature: 0.7
    },
    {
      headers: {
        'Content-Type': 'application/json',
        'api-key': AZURE_OPENAI_API_KEY,
      },
      timeout: 60000,
    }
  );

  return response.data.choices[0]?.message?.content || 'No se pudo generar el informe profesional.';
}

// Función para generar informe básico sin IA
function generateBasicReport(preferences: any, minigames: any[], cvAnalysis: any): string {
  const highSkills = minigames.filter(skill => skill.level === 'Alto');
  const mediumSkills = minigames.filter(skill => skill.level === 'Medio');
  const lowSkills = minigames.filter(skill => skill.level === 'Bajo');

  const totalScore = minigames.reduce((sum, skill) => sum + (skill.score || 0), 0) / Math.max(1, minigames.length);
  
  const level = totalScore >= 80 ? 'Alta empleabilidad' : totalScore >= 50 ? 'Empleabilidad media' : 'Baja empleabilidad';

  return `# Informe de Empleabilidad - Análisis Básico

---

## 1. Análisis del CV

**Estructura:** ${cvAnalysis?.structure || 'Regular'}  
**Coherencia:** ${cvAnalysis?.coherence || 'Regular'}  
**Experiencia:** ${cvAnalysis?.experience || 'Regular'}  

**Habilidades detectadas:** ${cvAnalysis?.skills?.join(', ') || 'No detectadas'}  

**Fortalezas:** ${cvAnalysis?.strengths?.join(', ') || 'No identificadas'}  

**Áreas de mejora:** ${cvAnalysis?.weaknesses?.join(', ') || 'No identificadas'}  

---

## 2. Puntos Fuertes

${highSkills.length > 0 ? `**Habilidades destacadas:** ${highSkills.map(s => s.skill).join(', ')}` : '**Necesitas desarrollar más habilidades blandas**'}  

${preferences?.areas?.length > 0 ? `**Áreas de interés:** ${preferences.areas.join(', ')}` : ''}  

---

## 3. Áreas de Desarrollo

${lowSkills.length > 0 ? `**Habilidades a mejorar:** ${lowSkills.map(s => s.skill).join(', ')}` : '**Todas las habilidades están en buen nivel**'}  

**Recomendación:** Practica regularmente los minijuegos para mejorar tus habilidades  

---

## 4. Recomendaciones Laborales

**Nivel de empleabilidad:** ${level}  

**Roles sugeridos:**
• Desarrollador frontend  
• Soporte técnico  
• Analista de datos  

**Modo de trabajo preferido:** ${preferences?.workMode || 'No especificado'}  

---

## 5. Próximos Pasos

### Esta semana:
• Completa todos los minijuegos disponibles  

### En 1 mes:
• Actualiza tu CV con las mejoras sugeridas  

### En 3 meses:
• Busca oportunidades laborales en las áreas de tu interés  

---

*Este es un informe básico generado automáticamente. Para un análisis más detallado, contacta con un orientador laboral.*`;
} 
