// src/features/personal/__tests__/report.fixture.ts

export const mockEmployabilityReport = {
  userId: 'user-ester-2025',
  fullName: 'Ester Pérez',

  // Habilidades blandas evaluadas
  softSkills: [
    {
      skill: 'Toma de decisiones',
      level: 'Alto',
      confidence: 0.9,
      feedback: 'Siempre eliges rápido y bien',
      interactions: []
    },
    {
      skill: 'Resolución de problemas',
      level: 'Medio',
      confidence: 0.65,
      feedback: 'A veces necesitas apoyo adicional',
      interactions: []
    },
    {
      skill: 'Gestión emocional',
      level: 'Bajo',
      confidence: 0.4,
      feedback: 'Necesitas más estrategias para controlar frustración',
      interactions: []
    },
    {
      skill: 'Comunicación',
      level: 'Alto',
      confidence: 0.85,
      feedback: 'Muy buena expresión clara y empática',
      interactions: []
    },
    {
      skill: 'Trabajo en equipo',
      level: 'Medio',
      confidence: 0.7,
      feedback: 'Colaboras bien, pero puedes mejorar coordinación',
      interactions: []
    },
    {
      skill: 'Autonomía',
      level: 'Bajo',
      confidence: 0.35,
      feedback: 'Demasiada dependencia de ayuda externa',
      interactions: []
    },
    {
      skill: 'Gestión del tiempo',
      level: 'Medio',
      confidence: 0.6,
      feedback: 'Organizas tareas, pero con retrasos frecuentes',
      interactions: []
    },
    {
      skill: 'Flexibilidad operativa',
      level: 'Alto',
      confidence: 0.88,
      feedback: 'Te adaptas bien a cambios inesperados',
      interactions: []
    },
    {
      skill: 'Pensamiento crítico',
      level: 'Medio',
      confidence: 0.65,
      feedback: 'Buena base, pero debes profundizar más',
      interactions: []
    },
    {
      skill: 'Orientación al detalle',
      level: 'Bajo',
      confidence: 0.4,
      feedback: 'Algunos errores evitables',
      interactions: []
    }
  ],

  // Puntaje global de empleabilidad
  employabilityScore: 75,

  // Preferencias laborales
  jobPreferences: {
    areas: ['Desarrollo web', 'Soporte técnico'],
    needs: ['Horario flexible', 'Herramientas accesibles'],
    workMode: 'remoto',
    availability: 'mañana',
    willingToRelocate: false,
    hasDisabilityCert: true,
    accessibilitySettings: {
      easyReadingMode: true,
      audioAssistiveMode: false,
      showPictograms: true,
      contrastLevel: 'alto',
      fontScale: 120
    }
  },

  // Análisis del CV
  cvAnalysis: {
    score: 62,
    strengths: ['Formato claro', 'Experiencia relevante'],
    weaknesses: ['Falta objetivos profesionales', 'No menciona habilidades blandas'],
    feedback:
      'Tu CV muestra experiencia, pero necesita mayor claridad en objetivos y desarrollo profesional'
  },

  // Información de juegos completados
  completedGames: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],

  // Recomendaciones personalizadas
  recommendations: {
    roles: ['Desarrollador frontend', 'Soporte técnico'],
    resources: ['Platzi', 'Cursos de Microsoft Learn'],
    cvImprovements: ['Incluir objetivos profesionales', 'Destacar soft skills'],
    nextSteps: ['Completar todos los juegos', 'Actualizar tu CV', 'Revisar tus preferencias']
  },

  // Fecha de generación
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),

  // Nivel de empleabilidad (bajo/media/alta)
  level: 'Empleabilidad media',
}