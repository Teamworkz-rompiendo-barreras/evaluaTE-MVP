// src/features/personal/__tests__/personalSlice.test.tsx
import { describe, it, expect } from 'vitest';
import { personalSlice } from '../personalSlice';

const initialState = personalSlice.getInitialState();

describe('personalSlice', () => {
  it('debe inicializar con valores predeterminados', () => {
    const initialState = personalSlice.getInitialState();
    expect(initialState).toEqual({
      firstName: '',
      lastName: '',
      email: '',
      whatsapp: '',
      jobPreferences: '',
      workMode: 'remoto',
      availability: 'completa',
      startDate: 'inmediata',
      willingToRelocate: false,
      hasDisabilityCert: false,
      cvFile: null,
      cvAnalysis: undefined,
      softSkills: [],
      unlockedGames: 1,
      report: undefined,
      logs: [],
      accessibilitySettings: {
        easyReadingMode: false,
        audioAssistiveMode: false,
        showPictograms: false,
        contrastLevel: 'normal',
        fontScale: 120,
      },
      completed: false,
    });
  });

  it('debe guardar datos personales correctamente', () => {
    const state = personalSlice.getInitialState();
    const action = personalSlice.actions.saveContact({
      firstName: 'Juan',
      lastName: 'Pérez',
      email: 'juan@example.com',
      whatsapp: '123456789',
    });

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      firstName: 'Juan',
      lastName: 'Pérez',
      email: 'juan@example.com',
      whatsapp: '123456789',
      unlockedGames: 1,
      completed: false, // Solo será true si también hay preferencias laborales
    });
  });

  it('debe guardar preferencias laborales correctamente', () => {
    const state = personalSlice.getInitialState();
    const action = personalSlice.actions.savePreferences({
      jobPreferences: 'Logística',
      workMode: 'presencial',
      availability: 'completa',
      startDate: 'inmediata',
      willingToRelocate: false,
      hasDisabilityCert: false,
    });

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      jobPreferences: 'Logística',
      workMode: 'presencial',
      availability: 'completa',
      startDate: 'inmediata',
      willingToRelocate: false,
      hasDisabilityCert: false,
      unlockedGames: 1,
      completed: false, // Solo será true si también hay datos de contacto
    });
  });

  it('debe guardar archivo del CV correctamente', () => {
    const state = personalSlice.getInitialState();
    const mockFilePayload = { fileName: 'example.pdf', fileContent: '' };
    const action = personalSlice.actions.saveCV(mockFilePayload);

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      cvFile: mockFilePayload,
      unlockedGames: 2,
    });
  });

  it('debe guardar análisis del CV correctamente', () => {
    const state = personalSlice.getInitialState();
    const mockCvAnalysis = { structure: 'bueno', coherence: 'bueno', experience: 'regular', skills: ['Comunicación', 'Trabajo en equipo'] };
    const action = personalSlice.actions.saveCvAnalysis(mockCvAnalysis);

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      cvAnalysis: mockCvAnalysis,
      unlockedGames: 2,
    });
  });

  it('debe desbloquear el siguiente minijuego correctamente', () => {
    const state = personalSlice.getInitialState();
    const action = personalSlice.actions.unlockNextGame();

    const newState = personalSlice.reducer(state, action);
    expect(newState).toEqual({
      ...initialState,
      unlockedGames: 2,
    });
  });
});