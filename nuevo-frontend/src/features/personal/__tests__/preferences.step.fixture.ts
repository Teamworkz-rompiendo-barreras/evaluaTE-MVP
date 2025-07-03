// src/features/personal/__tests__/preferences.step.fixture.ts

import type { JobPreference } from '@/types/preferences'

// Si mockUser no existe, define un mock local:
const mockUser = {
  jobPreferences: {
    areas: ['Desarrollo web'],
    needs: ['Horario flexible', 'Acceso remoto'],
    workMode: 'remoto',
    availability: 'mañana',
    willingToRelocate: false,
    hasDisabilityCert: true,
  }
};

const preferencesFixture: JobPreference = {
  areas: mockUser.jobPreferences.areas,
  needs: mockUser.jobPreferences.needs,
  workMode: mockUser.jobPreferences.workMode,
  availability: mockUser.jobPreferences.availability,
  willingToRelocate: mockUser.jobPreferences.willingToRelocate,
  hasDisabilityCert: mockUser.jobPreferences.hasDisabilityCert,
}

export default preferencesFixture