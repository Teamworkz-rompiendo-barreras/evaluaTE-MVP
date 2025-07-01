// src/features/personal/__tests__/report.fixture.ts
import type { EmployabilityReport } from '@/types/skills'

export const mockEmployabilityReport: EmployabilityReport = {
  userId: 'user-ester-123',
  fullName: 'Ester García',
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
      skill: 'Gestión del tiempo',
      level: 'Bajo',
      confidence: 0.4,
      feedback: 'Evita dejar cosas pendientes'
    }
  ],
  employabilityScore: 75,
  jobPreferences: {
    areas: ['Desarrollo web', 'UX'],
    needs: ['Horario flexible', 'Herramientas accesibles'],
    workMode: 'remoto',
    availability: 'mañana',
    willingToRelocate: false,
    hasDisabilityCert: true
  },
  createdAt: new Date().toISOString(),
  completedGames: [1, 2, 3, 4, 5]
}