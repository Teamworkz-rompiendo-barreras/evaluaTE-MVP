// src/pages/GameScenePage.tsx
import React, { useEffect } from 'react'

import { useParams, useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'

// Importamos datos del juego
import { useGetSceneQuery } from '../features/games/scenesApi'
import { useGameController } from '../features/games/useGameController'
import GameScene from '../components/GameScene'
import ProgressBar from '../components/ProgressBar'
import { RootState } from '../app/store'

const GameScenePage: React.FC = () => {
  const { gameId } = useParams<{ gameId: string }>()
  const navigate = useNavigate()

  // Estado del juego
  const { currentGame, currentScene, gameProgress } = useGameController()
  
  // Estado de accesibilidad
  const accessibility = useSelector((state: RootState) => state.accessibility)
  
  // Estado de personal
  const personal = useSelector((state: RootState) => state.personal)

  const {
    data: scene,
    isLoading,
    isError
  } = useGetSceneQuery(gameId ?? '', { skip: !gameId })

  const {
    startGame,
    completeScene,
    goToScene
  } = useGameController()

  useEffect(() => {
    if (gameId && !currentGame) {
      startGame(gameId)
    }
  }, [gameId, currentGame, startGame])

  useEffect(() => {
    if (!personal?.firstName || !personal?.lastName) {
      navigate('/datos-personales')
      return
    }
    
    if (!personal?.jobPreferences) {
      navigate('/preferencias')
      return
    }
  }, [personal, navigate])

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
            Volver al menú
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
              current={gameProgress.current} 
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
            accessibility={{
              contrastLevel: accessibility.contrastLevel === 'alto' || accessibility.contrastLevel === 'muy-alto' ? 'high' : 'normal',
              fontScale: accessibility.fontScale,
              audioEnabled: accessibility.audioAssistiveMode,
              visualHelp: accessibility.showPictograms,
              timeExtensions: true
            }}
          />
        </div>

        {/* Navegación */}
        <div className="mt-8 flex justify-between">
          <button
            onClick={() => navigate('/games')}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            ← Volver al menú
          </button>
        </div>
      </div>
    </div>
  )
}

export default GameScenePage