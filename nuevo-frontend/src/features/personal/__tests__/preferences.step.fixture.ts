// src/features/personal/__tests__/preferences.step.fixture.ts

import type { JobPreference } from '@/types/preferences'
import { mockUser } from '@/__fixtures__/user.fixtures'

const preferencesFixture: JobPreference = {
  areas: mockUser.jobPreferences.areas || ['Desarrollo web'],
  needs: mockUser.jobPreferences.needs || ['Horario flexible', 'Acceso remoto'],
  workMode: mockUser.jobPreferences.workMode || 'remoto',
  availability: mockUser.jobPreferences.availability || 'mañana',
  willingToRelocate: mockUser.jobPreferences.willingToRelocate || false,
  hasDisabilityCert: mockUser.jobPreferences.hasDisabilityCert || true,
}

export default preferencesFixture