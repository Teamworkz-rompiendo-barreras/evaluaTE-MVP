// src/features/personal/__tests__/report.fixture.ts

import type {
  EmployabilityReport,
  CvAnalysis,
  SoftSkillResult,
  JobPreference,
  GameDecisionLog
} from '@/types/skills'
import type { AccessibilitySettings } from '@/types/preferences'

export const mockEmployabilityReport: EmployabilityReport = {
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
      contrastLevel: 'alto'
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

  // Logs del juego para análisis posterior
  logs: [
    {
      sceneId: 1,
      decisions: [
        {
          sceneId: 1,
          stepIndex: 0,
          optionText: 'Respondes de inmediato',
          isCorrect: true,
          skillImpacts: { 'Toma de decisiones': 0.9 },
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          screenResolution: `${window.screen.width}x${window.screen.height}`,
          timeSpent: 120,
          retries: 0,
          emotionalState: 'positivo'
        },
        {
          sceneId: 1,
          stepIndex: 1,
          optionText: 'Organizas según prioridad',
          isCorrect: true,
          skillImpacts: { 'Resolución de problemas': 0.8 },
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          screenResolution: `${window.screen.width}x${window.screen.height}`,
          timeSpent: 180,
          retries: 1,
          emotionalState: 'neutro'
        }
      ],
      totalSteps: 5,
      totalTime: 1200,
      averageConfidence: 0.75,
      emotionalTrend: ['positivo', 'neutro', 'positivo', 'neutro', 'positivo'],
      accessibilityUsed: true,
      accessibilitySettings: {
        easyReadingMode: true,
        audioAssistiveMode: false,
        showPictograms: true,
        contrastLevel: 'alto'
      }
    },
    {
      sceneId: 3,
      decisions: [
        {
          sceneId: 3,
          stepIndex: 0,
          optionText: 'Llamas a soporte técnico',
          isCorrect: false,
          skillImpacts: { 'Autonomía': 0.4 },
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          screenResolution: `${window.screen.width}x${window.screen.height}`,
          timeSpent: 200,
          retries: 2,
          emotionalState: 'negativo'
        },
        {
          sceneId: 3,
          stepIndex: 1,
          optionText: 'Reinicias el equipo',
          isCorrect: true,
          skillImpacts: { 'Gestión del tiempo': 0.75 },
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          screenResolution: `${window.screen.width}x${window.screen.height}`,
  timeSpent: 150,
  retries: 0,
  emotionalState: 'positivo'
}
],
totalSteps: 10,
totalTime: 3600,
averageConfidence: 0.7,
emotionalTrend: Array(10).fill('positivo').map((_, i) => i % 3 === 0 ? 'negativo' : 'positivo'),
accessibilityUsed: true,
accessibilitySettings: {
  easyReadingMode: true,
  audioAssistiveMode: false,
  showPictograms: true,
  contrastLevel: 'alto'
}
    }
  ]
}