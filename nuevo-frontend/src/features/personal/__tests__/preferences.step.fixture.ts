// src/features/personal/__tests__/preferences.step.fixture.ts
import { mockUser } from '@/__fixtures__/user.fixtures'

const preferencesFixture = {
  jobPreferences: mockUser.jobPreferences,
  workMode: mockUser.jobPreferences.workMode,
  availability: mockUser.jobPreferences.availability,
  willingToRelocate: mockUser.jobPreferences.willingToRelocate,
  hasDisabilityCert: mockUser.jobPreferences.hasDisabilityCert
}

export default preferencesFixture