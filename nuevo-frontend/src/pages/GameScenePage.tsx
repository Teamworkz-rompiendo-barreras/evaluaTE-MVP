// src/pages/GameScenePage.tsx
import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { useParams, useNavigate } from 'react-router-dom'

// Importamos datos del juego
import { useGetSceneQuery } from '../features/games/scenesApi'
import { useGameController } from '../features/games/useGameController'
import { useAppDispatch, useAppSelector } from '../app/hooks'
import { markGameComplete } from '../features/progress/progressSlice'
import { unlockNextGame } from '../features/personal/personalSlice'
import { saveSoftSkills } from '../features/personal/personalSlice'

// Hook para guardar logs de usuario
import { useLogger } from '../features/games/useLogger'

export default function GameScenePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()

  // Accesibilidad
  const accessibilityState = useAppSelector((state) => state.accessibility)

  // Escena actual desde JSON
  const {
    data: scene,
    isLoading,
    isError
  } = useGetSceneQuery(id ?? '', { skip: !id })

  const stepsCount = scene?.steps.length ?? 0
  const { currentStep, timeLeft, goNext, goPrev } = useGameController(stepsCount)
  const { logStep, logSoftSkill, logFinalGame } = useLogger()

  // Estado local del juego
  const [selectedOptions, setSelectedOptions] = useState<number[]>([])
  const [showFeedback, setShowFeedback] = useState(false)

  if (isLoading) {
    return (
      <main className="flex items-center justify-center min-h-screen">
        <p>Cargando escena…</p>
      </main>
    )
  }

  if (isError || !scene) {
    return (
      <main className="flex flex-col items-center justify-center min-h-screen gap-6">
        <p className="text-lg font-semibold text-red-600">Error al cargar la escena.</p>
        <p>Este minijuego aún no está disponible. Vuelve al menú de minijuegos.</p>
        <button
          className="py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          onClick={() => navigate('/games')}
        >
          Volver al menú de minijuegos
        </button>
      </main>
    )
  }

  const gameNum = Number(id)
  const currentScene = scene.steps[currentStep]

  // Calculamos softSkills al finalizar todas las escenas
  const handleFinishGame = () => {
    const skillResults = [
      {
        skill: getSkillNameFromGameId(gameNum),
        level: calculateLevel(),
        confidence: calculateConfidence(),
      },
    ]

    // Guardamos en Redux
    dispatch(saveSoftSkills(skillResults))
    dispatch(markGameComplete(String(gameNum)))
    dispatch(unlockNextGame())

    // Registramos en backend
    logFinalGame(gameNum, skillResults)
    
    // Navegamos al siguiente juego o resultados
    navigate(`/games/${gameNum + 1}`) // TODO: ir a `/resultados` si es el último juego
  }

  // Mapea ID del juego a nombre de habilidad blanda
  const getSkillNameFromGameId = (id: number): string => {
    switch (id) {
      case 1:
        return 'Toma de decisiones'
      case 2:
        return 'Resolución de problemas'
      case 3:
        return 'Trabajo en equipo'
      case 4:
        return 'Gestión emocional'
      case 5:
        return 'Comunicación'
      case 6:
        return 'Curiosidad y aprendizaje continuo'
      case 7:
        return 'Creatividad'
      case 8:
        return 'Flexibilidad'
      case 9:
        return 'Pensamiento crítico'
      case 10:
        return 'Autonomía'
      default:
        return 'Habilidad desconocida'
    }
  }

  // Calcula nivel (Alto/Medio/Bajo) según decisiones, tiempo y consistencia
  const calculateLevel = (): 'Bajo' | 'Medio' | 'Alto' => {
    // Aquí iría lógica real basada en decisiones + tiempo + uso de ayuda
    // Ejemplo básico: si hay más de 2 errores → Medio / Bajo
    const totalErrors = selectedOptions.filter((opt) =>
      currentScene.options && !currentScene.options[opt]?.isCorrect
    ).length

    if (totalErrors === 0) return 'Alto'
    if (totalErrors <= 2) return 'Medio'
    return 'Bajo'
  }

  // Calcula confianza numérica (0 - 1) para gráfico radar
  const calculateConfidence = (): number => {
    // Por ahora usamos un cálculo simple
    const correctAnswers = selectedOptions.filter((opt) =>
      currentScene.options && currentScene.options[opt]?.isCorrect
    ).length

    return Math.max(0.1, correctAnswers / stepsCount)
  }

  // Manejo de selección de opción
  const handleSelectOption = async (optionIndex: number) => {
    const option = currentScene.options?.[optionIndex]
    const timeSpent = 30 - timeLeft

    // Guardamos respuesta localmente
    const updatedSelections = [...selectedOptions]
    updatedSelections[currentStep] = optionIndex
    setSelectedOptions(updatedSelections)
    setShowFeedback(true)

    // Registramos log de paso en backend
    await logStep({
      gameId: gameNum,
      stepIndex: currentStep,
      optionIndex,
      timeSpent,
      usedHelp: false, // esto podría venir de un botón "ayuda" opcional
      emotionalResponse: option?.feedback || null,
    })

    setTimeout(() => {
      setShowFeedback(false)
      if (currentStep < stepsCount - 1) {
        goNext()
      }
    }, 1000)
  }

  if (isLoading) {
    return (
      <main className="flex items-center justify-center min-h-screen">
        <p>Cargando escena…</p>
      </main>
    )
  }

  if (isError || !scene) {
    return (
      <main className="flex flex-col items-center justify-center min-h-screen gap-6">
        <p className="text-lg font-semibold text-red-600">Error al cargar la escena.</p>
        <p>Este minijuego aún no está disponible. Vuelve al menú de minijuegos.</p>
        <button
          className="py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          onClick={() => navigate('/games')}
        >
          Volver al menú de minijuegos
        </button>
      </main>
    )
  }

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4 space-y-6">
      {/* Título */}
      <h2
        className={`text-xl font-bold ${
          accessibilityState.highContrast ? 'bg-black text-white p-2' : ''
        }`}
      >
        {scene.title}
      </h2>

      {/* Barra de progreso visual */}
      <div className="w-full max-w-sm bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-green-600 h-2.5 rounded-full"
          style={{
            width: `${((currentStep + 1) / stepsCount) * 100}%`,
          }}
        ></div>
      </div>

      {/* Tiempo restante */}
      <div className="font-medium">
        ⏱️ Tiempo restante:{' '}
        <span
          className={
            accessibilityState.highContrast ? 'bg-yellow-100 p-1' : ''
          }
        >
          {timeLeft}s
        </span>
      </div>

      {/* Texto de escena */}
      <div className="mb-6 max-w-md text-center">
        <p
          className={`text-lg ${
            accessibilityState.fontScale > 100 ? 'text-xl' : ''
          }`}
        >
          {currentScene.text}
        </p>
      </div>

      {/* Imagen opcional */}
      {currentScene.image && (
        <img
          src={`/api/scenes/${currentScene.image}`}
          alt={`Escena ${currentStep + 1}`}
          className="max-w-xs mb-6"
          onError={(e) => {
            e.currentTarget.src = '/icons/fallback.svg'
          }}
        />
      )}

      {/* Opciones */}
      <div className="space-y-3 w-full max-w-sm">
        {Array.isArray(currentScene.options) &&
          currentScene.options.map((option, idx) => (
            <button
              key={idx}
              onClick={() => handleSelectOption(idx)}
              className={`w-full text-left p-3 border rounded hover:bg-gray-100 ${
                accessibilityState.highContrast ? 'bg-gray-800 text-white' : ''
              }`}
            >
              {option.text}
            </button>
          ))}
      </div>

      {/* Feedback positivo */}
      {showFeedback && (
        <div className="absolute top-4 right-4 bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded shadow-lg animate-pulse">
          ¡Gran elección!
        </div>
      )}

      {/* Controles */}
      <div className="flex gap-4 mt-4">
        <button
          onClick={goPrev}
          disabled={currentStep === 0}
          className="py-2 px-4 bg-gray-300 text-gray-700 rounded disabled:opacity-50"
        >
          Atrás
        </button>

        {currentStep < stepsCount - 1 ? (
          <button
            onClick={() => {
              if (selectedOptions[currentStep] !== undefined) {
                goNext()
                setShowFeedback(false)
              } else {
                toast.error('Debes elegir una opción')
              }
            }}
            className="py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            Siguiente
          </button>
        ) : (
          <button
            onClick={handleFinishGame}
            className="py-2 px-4 bg-green-600 text-white rounded hover:bg-green-700 transition"
          >
            Finalizar
          </button>
        )}
      </div>
    </main>
  )
}