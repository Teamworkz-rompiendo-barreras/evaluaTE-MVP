// src/features/personal/__tests__/personalSlice.test.tsx

import { renderHook } from '@testing-library/react'
import { useAppSelector } from '@/app/hooks'
import personalSlice, { saveContact, savePreferences, generateFinalReport } from '../personalSlice'

describe('personalSlice', () => {
  const initialState = {
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
    report: undefined
  }

  it('debería actualizar datos personales correctamente', () => {
    const state = personalSlice(initialState, saveContact({
      firstName: 'Ester',
      lastName: 'García',
      email: 'ester@example.com',
      whatsapp: '987654321'
    }))

    expect(state.firstName).toBe('Ester')
    expect(state.lastName).toBe('García')
    expect(state.email).toBe('ester@example.com')
    expect(state.whatsapp).toBe('987654321')
  })

  it('debería guardar preferencias laborales como objeto completo', () => {
    const preferences = {
      jobPreferences: 'Desarrollo web',
      workMode: 'remoto',
      availability: 'mañana',
      startDate: 'inmediata',
      willingToRelocate: true,
      hasDisabilityCert: false
    }

    const state = personalSlice(initialState, savePreferences(preferences))

    expect(state.jobPreferences).toEqual(expect.objectContaining({
      areas: ['Desarrollo web'],
      needs: [],
      workMode: 'remoto',
      availability: 'mañana',
      willingToRelocate: true,
      hasDisabilityCert: false
    }))
  })

  it('debería calcular puntaje global de empleabilidad correctamente', () => {
    const stateWithSkills = {
      ...initialState,
      softSkills: [
        { skill: 'Toma de decisiones', level: 'Alto', confidence: 0.9 },
        { skill: 'Resolución de problemas', level: 'Medio', confidence: 0.65 },
        { skill: 'Gestión emocional', level: 'Bajo', confidence: 0.4 },
        { skill: 'Comunicación', level: 'Alto', confidence: 0.85 },
        { skill: 'Trabajo en equipo', level: 'Medio', confidence: 0.7 },
        { skill: 'Autonomía', level: 'Bajo', confidence: 0.35 },
        { skill: 'Gestión del tiempo', level: 'Medio', confidence: 0.6 },
        { skill: 'Flexibilidad operativa', level: 'Alto', confidence: 0.88 },
        { skill: 'Pensamiento crítico', level: 'Medio', confidence: 0.65 },
        { skill: 'Orientación al detalle', level: 'Bajo', confidence: 0.4 }
      ],
      cvAnalysis: {
        score: 62,
        strengths: ['Formato claro', 'Experiencia relevante'],
        weaknesses: ['Falta de objetivos profesionales']
      }
    }

    // Simulamos el dispatch manualmente
    const updatedState = personalSlice(stateWithSkills, generateFinalReport())

    // Verifica que se haya generado el informe
    expect(updatedState.report).toBeDefined()
    expect(updatedState.report?.fullName).toBe('Ester Pérez')

    // Verifica puntaje ajustado por IA
    expect(updatedState.report?.employabilityScore).toBe(75)
    expect(updatedState.report?.level).toBe('Alta empleabilidad')
  })

  it('debería manejar reinicio del estado correctamente', () => {
    const stateWithCV = personalSlice(initialState, savePreferences({
      jobPreferences: 'Desarrollo web',
      workMode: 'remoto',
      availability: 'mañana',
      startDate: 'inmediata',
      willingToRelocate: true,
      hasDisabilityCert: false
    }))

    // Simular carga de CV
    const stateWithReport = personalSlice(stateWithCV, generateFinalReport())

    // Reiniciar estado
    const resetState = personalSlice(stateWithReport, { type: 'RESET' })

    expect(resetState.firstName).toBe('')
    expect(resetState.cvAnalysis).toBeUndefined()
    expect(resetState.report).toBeUndefined()
  })
})