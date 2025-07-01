// src/features/games/__tests__/useGameController.test.tsx
import { renderHook, act } from '@testing-library/react'
import useGameController from '@/features/games/useGameController'

describe('useGameController', () => {
  it('debería iniciar con estado inicial correcto', () => {
    const { result } = renderHook(() => useGameController())

    expect(result.current.currentStep).toBe(0)
    expect(result.current.choices).toEqual([])
    expect(result.current.completed).toBe(false)
    expect(result.current.progress).toBe(0)
  })

  it('debería avanzar al siguiente paso correctamente', () => {
    const { result } = renderHook(() => useGameController())

    act(() => {
      result.current.nextStep()
    })

    expect(result.current.currentStep).toBe(1)
    expect(result.current.progress).toBe(20) // 1 de 5 pasos → ~20%
  })

  it('debería retroceder al paso anterior', () => {
    const { result } = renderHook(() => useGameController())

    act(() => {
      result.current.nextStep()
      result.current.prevStep()
    })

    expect(result.current.currentStep).toBe(0)
    expect(result.current.progress).toBe(0)
  })

  it('debería registrar una decisión cuando se selecciona una opción', () => {
    const { result } = renderHook(() => useGameController())

    const choice = {
      sceneId: 1,
      stepIndex: 0,
      optionText: 'Respuesta correcta',
      isCorrect: true,
      skillImpacts: { 'Toma de decisiones': 0.9 },
      timestamp: new Date().toISOString(),
    }

    act(() => {
      result.current.makeChoice(choice)
    })

    expect(result.current.choices).toContainEqual(choice)
    expect(result.current.choices.length).toBe(1)
  })

  it('debería completar el minijuego tras 5 decisiones', () => {
    const { result } = renderHook(() => useGameController())

    act(() => {
      for (let i = 0; i < 5; i++) {
        result.current.makeChoice({
          sceneId: 1,
          stepIndex: i,
          optionText: `Respuesta ${i}`,
          isCorrect: i % 2 === 0,
          skillImpacts: { 'Resolución de problemas': i % 2 === 0 ? 0.8 : 0.4 },
          timestamp: new Date().toISOString(),
        })
        if (i < 4) result.current.nextStep()
      }
    })

    expect(result.current.completed).toBe(true)
    expect(result.current.progress).toBe(100)
  })

  it('debería reiniciar el juego correctamente', () => {
    const { result } = renderHook(() => useGameController())

    act(() => {
      result.current.nextStep()
      result.current.resetGame()
    })

    expect(result.current.currentStep).toBe(0)
    expect(result.current.choices).toEqual([])
    expect(result.current.completed).toBe(false)
    expect(result.current.progress).toBe(0)
  })

  it('debería calcular puntaje promedio de habilidades blandas', () => {
    const { result } = renderHook(() => useGameController())

    act(() => {
      result.current.makeChoice({
        sceneId: 1,
        stepIndex: 0,
        optionText: 'Opción A',
        isCorrect: true,
        skillImpacts: { 'Toma de decisiones': 0.9 },
        timestamp: new Date().toISOString(),
      })

      result.current.makeChoice({
        sceneId: 1,
        stepIndex: 1,
        optionText: 'Opción B',
        isCorrect: false,
        skillImpacts: { 'Pensamiento crítico': 0.6 },
        timestamp: new Date().toISOString(),
      })
    })

    const scores = result.current.getSkillScores()

    expect(scores['Toma de decisiones']).toBe(0.9)
    expect(scores['Pensamiento crítico']).toBe(0.6)
  })
})