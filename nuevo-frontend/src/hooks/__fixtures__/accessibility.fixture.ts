// src/hooks/__fixtures__/accessibility.fixture.ts
import type { AccessibilitySettings } from '@/features/personal/personalSlice'

export const accessibilityFixture: AccessibilitySettings = {
  easyReadingMode: true,
  audioAssistiveMode: false,
  showPictograms: true,
  contrastLevel: 'alto'
}