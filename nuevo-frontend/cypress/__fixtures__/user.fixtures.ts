// cypress/__fixtures__/user.fixtures.ts

import type {
  JobPreference,
  AccessibilitySettings
} from '../../src/types/preferences'



export const mockUser = {
  firstName: 'Ester',
  lastName: 'García',
  email: 'ester@example.com',
  whatsapp: '987654321',
  jobPreferences: {
    areas: ['Desarrollo web', 'UX'],
    needs: ['Horario flexible', 'Acceso a herramientas de accesibilidad'],
    workMode: 'remoto',
    availability: 'mañana',
    willingToRelocate: false,
    hasDisabilityCert: true
  } satisfies JobPreference,
  accessibilitySettings: {
    easyReadingMode: true,
    audioAssistiveMode: false,
    showPictograms: true,
    contrastLevel: 'alto'
  } satisfies AccessibilitySettings,
  cvFile: 'cv.pdf',
  completedGames: [1, 2, 3, 4, 5],
  softSkills: [
    { skill: 'Toma de decisiones', level: 'Alto', confidence: 0.9 },
    { skill: 'Resolución de problemas', level: 'Medio', confidence: 0.65 },
    { skill: 'Comunicación', level: 'Bajo', confidence: 0.4 }
  ],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString()
}