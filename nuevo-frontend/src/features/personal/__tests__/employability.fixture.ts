// src/features/personal/__tests__/employability.fixture.ts

import type {
  EmployabilityReport,
  SoftSkillResult,
  JobPreference,
  CvAnalysis
} from '@/types/skills'

export const mockEmployabilityReport: EmployabilityReport = {
  userId: 'user-ester-2025',
  fullName: 'Ester Pérez',

  softSkills: [
    {
      skill: 'Toma de decisiones',
      level: 'Alto',
      confidence: 0.9,
      feedback: 'Siempre eliges rápido y bien'
    },
    {
      skill: 'Resolución de problemas',
      level: 'Medio',
      confidence: 0.65,
      feedback: 'A veces necesitas apoyo adicional'
    },
    {
      skill: 'Gestión emocional',
      level: 'Bajo',
      confidence: 0.4,
      feedback: 'Necesitas más estrategias para controlar frustración'
    },
    {
      skill: 'Comunicación',
      level: 'Alto',
      confidence: 0.85,
      feedback: 'Muy buena expresión clara y empática'
    },
    {
      skill: 'Trabajo en equipo',
      level: 'Medio',
      confidence: 0.7,
      feedback: 'Colaboras bien, pero puedes mejorar coordinación'
    },
    {
      skill: 'Autonomía',
      level: 'Bajo',
      confidence: 0.35,
      feedback: 'Demasiada dependencia de ayuda externa'
    },
    {
      skill: 'Gestión del tiempo',
      level: 'Medio',
      confidence: 0.6,
      feedback: 'Organizas tareas, pero con retrasos frecuentes'
    },
    {
      skill: 'Flexibilidad operativa',
      level: 'Alto',
      confidence: 0.88,
      feedback: 'Te adaptas bien a cambios inesperados'
    },
    {
      skill: 'Pensamiento crítico',
      level: 'Medio',
      confidence: 0.65,
      feedback: 'Buena base, pero debes profundizar más'
    },
    {
      skill: 'Orientación al detalle',
      level: 'Bajo',
      confidence: 0.4,
      feedback: 'Algunos errores evitables'
    }
  ],

  employabilityScore: 75,

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

  cvAnalysis: {
    score: 62,
    strengths: ['Formato claro', 'Experiencia laboral destacada'],
    weaknesses: ['Falta objetivos profesionales', 'No menciona habilidades blandas'],
    feedback:
      'Tu CV muestra experiencia, pero necesita mayor claridad en objetivos y desarrollo profesional'
  },

  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  completedGames: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
}