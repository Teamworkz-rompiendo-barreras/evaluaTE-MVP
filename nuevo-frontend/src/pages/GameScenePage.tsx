// src/pages/GameScenePage.tsx
import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { useParams, useNavigate } from 'react-router-dom'
import { useGetSceneQuery } from '../features/games/scenesApi'
import { useGameController } from '../features/games/useGameController'
import { useAppDispatch, useAppSelector } from '../app/hooks'
import { markGameComplete } from '../features/progress/progressSlice'
import { unlockNextGame } from '../features/personal/personalSlice'
import { saveSoftSkills } from '../features/personal/personalSlice'

export default function GameScenePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()

  // Accesibilidad
  const accessibility = useAppSelector((state) => state.accessibility)

  // Escena actual
  const {
    data: scene,
    isLoading,
    isError
  } = useGetSceneQuery(id ?? '', { skip: !id })

  const stepsCount = scene?.steps.length ?? 0
  const { currentStep, timeLeft, goNext, goPrev } = useGameController(stepsCount)

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
    // Ejemplo de cálculo de habilidad blanda (esto debería venir del backend o IA)
    const skillResults = [
      {
        skill: getSkillNameFromGameId(gameNum),
        level: calculateLevel(), // Alto / Medio / Bajo
        confidence: calculateConfidence(), // entre 0 y 1
      },
    ]

    // Guardamos habilidades blandas
    dispatch(saveSoftSkills(skillResults))

    // Marcamos como completado y desbloqueamos siguiente
    dispatch(markGameComplete(String(gameNum)))
    dispatch(unlockNextGame())

    // Navegamos al siguiente juego o al dashboard
    navigate(`/games/${gameNum + 1}`) // Esto puede cambiar a `/resultados` si es el último
  }

  // Mapea ID del juego a nombre de habilidad
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
  const calculateLevel = (): 'Alto' | 'Medio' | 'Bajo' => {
    // Aquí iría lógica real basada en respuestas, tiempo, etc.
    return 'Alto'
  }

  // Calcula confianza numérica (0 - 1) para gráfico radar
  const calculateConfidence = (): number => {
    // Por ahora un valor fijo, pero debería ser dinámico
    return 0.92
  }

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4 space-y-6">
      {/* Título */}
      <h2 className={`text-xl font-bold ${accessibility.highContrast ? 'bg-black text-white p-2' : ''}`}>
        {scene.title}
      </h2>

      {/* Barra de progreso visual */}
      <div className="w-full max-w-sm bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-green-600 h-2.5 rounded-full"
          style={{ width: `${((currentStep + 1) / stepsCount) * 100}%` }}
        ></div>
      </div>

      {/* Tiempo restante */}
      <div className="font-medium">
        ⏱️ Tiempo restante:{' '}
        <span className={accessibility.highContrast ? 'bg-yellow-100 p-1' : ''}>
          {timeLeft}s
        </span>
      </div>

      {/* Texto de escena */}
      <div className="mb-6 max-w-md text-center">
        <p
          className={`text-lg ${
            accessibility.fontScale > 100 ? 'text-xl' : ''
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
              onClick={() => {
                handleSelectOption(idx)
              }}
              className={`w-full text-left p-3 border rounded hover:bg-gray-100 ${
                accessibility.highContrast ? 'bg-gray-800 text-white' : ''
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

  // Manejo de selección de opción
  function handleSelectOption(optionIndex: number) {
    const updatedSelections = [...selectedOptions]
    updatedSelections[currentStep] = optionIndex
    setSelectedOptions(updatedSelections)
    setShowFeedback(true)

    setTimeout(() => {
      setShowFeedback(false)
      if (currentStep < stepsCount - 1) {
        goNext()
      }
    }, 1000)
  }
}