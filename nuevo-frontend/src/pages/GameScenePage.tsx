// src/pages/GameScenePage.tsx
import React, { useEffect } from 'react'
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
import GameScene from '../components/GameScene'
import ProgressBar from '../components/ProgressBar'

const GameScenePage: React.FC = () => {
  const { gameId } = useParams<{ gameId: string }>()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()

  // Accesibilidad
  const accessibilityState = useAppSelector((state) => state.accessibility)

  // Escena actual desde JSON
  const {
    data: scene,
    isLoading,
    isError
  } = useGetSceneQuery(gameId ?? '', { skip: !gameId })

  const stepsCount = scene?.steps.length ?? 0
  const { currentStep, timeLeft, nextStep, prevStep } = useGameController({ sceneId: Number(gameId) })
  const { logStep, logSoftSkill, logFinalGame } = useLogger()

  // Estado local del juego
  const [selectedOptions, setSelectedOptions] = useState<number[]>([])
  const [showFeedback, setShowFeedback] = useState(false)

  const {
    currentGame,
    currentScene,
    gameProgress,
    accessibility,
    startGame,
    completeScene,
    goToScene
  } = useGameController()

  useEffect(() => {
    if (gameId && !currentGame) {
      startGame(gameId)
    }
  }, [gameId, currentGame, startGame])

  const handleSceneComplete = (log: any) => {
    completeScene(log)
  }

  const handleNextScene = (sceneId: string) => {
    goToScene(sceneId)
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

  const gameNum = Number(gameId)
  const currentSceneData = scene.steps[currentStep]

  // Calculamos softSkills al finalizar todas las escenas
  const handleFinishGame = () => {
    const levelMap = {
      'Bajo': 'bajo',
      'Medio': 'medio',
      'Alto': 'alto',
    } as const;
    const skillResults = [
      {
        skill: getSkillNameFromGameId(gameNum),
        score: Math.round(calculateConfidence() * 100),
        level: levelMap[calculateLevel()],
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
      currentSceneData.options && !currentSceneData.options[opt]?.isCorrect
    ).length

    if (totalErrors === 0) return 'Alto'
    if (totalErrors <= 2) return 'Medio'
    return 'Bajo'
  }

  // Calcula confianza numérica (0 - 1) para gráfico radar
  const calculateConfidence = (): number => {
    // Por ahora usamos un cálculo simple
    const correctAnswers = selectedOptions.filter((opt) =>
      currentSceneData.options && currentSceneData.options[opt]?.isCorrect
    ).length

    return Math.max(0.1, correctAnswers / stepsCount)
  }

  // Manejo de selección de opción
  const handleSelectOption = async (optionIndex: number) => {
    const option = currentSceneData.options?.[optionIndex]
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
        nextStep()
      }
    }, 1000)
  }

  if (!currentGame) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Cargando juego...</h2>
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
        </div>
      </div>
    )
  }

  if (!currentScene) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">¡Juego completado!</h2>
          <p className="mb-4">Has terminado {currentGame.title}</p>
          <button
            onClick={() => navigate('/games')}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Volver al dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header del juego */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <span className="text-4xl mr-4">{currentGame.icon}</span>
            <div>
              <h1 className="text-3xl font-bold" style={{ color: currentGame.color }}>
                {currentGame.title}
              </h1>
              <p className="text-lg text-gray-600">{currentGame.subtitle}</p>
            </div>
          </div>
          
          {/* Barra de progreso */}
          <div className="mb-4">
            <ProgressBar 
              step={gameProgress.current} 
              total={gameProgress.total}
              label="Escena"
            />
          </div>
          
          {/* Información del día */}
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <p className="text-sm text-gray-600 mb-2">
              <strong>Día:</strong> {currentGame.day} | <strong>Escenario:</strong> {currentGame.scenario}
            </p>
            <p className="text-gray-700">{currentGame.description}</p>
          </div>
        </div>

        {/* Escena actual */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <GameScene
            scene={currentScene}
            onSceneComplete={handleSceneComplete}
            onNextScene={handleNextScene}
            accessibility={accessibility}
          />
        </div>

        {/* Navegación */}
        <div className="mt-8 flex justify-between">
          <button
            onClick={() => navigate('/games')}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            ← Volver al dashboard
          </button>
          
          <div className="text-sm text-gray-500">
            Escena {gameProgress.current} de {gameProgress.total}
          </div>
        </div>
      </div>
    </div>
  )
}

export default GameScenePage