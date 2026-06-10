// src/pages/GameScenePage.tsx
import React, { useEffect } from 'react'

import { useParams, useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'

// Importamos datos del juego
import { useGameController } from '../features/games/useGameController'
import GameScene from '../components/GameScene'
import ProgressBar from '../components/ProgressBar'

import { RootState } from '../app/store'
import { GameLog } from '../types/game';

const GameScenePage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  // Estado del juego — una sola llamada al hook
  const {
    currentGame,
    currentScene,
    gameProgress,
    startGame,
    completeScene,
    goToScene,
  } = useGameController()

  // Estado de accesibilidad
  const accessibility = useSelector((state: RootState) => state.accessibility)
  const completedGames = useSelector((state: RootState) => state.game.completedGames)
  const personal = useSelector((state: RootState) => state.personal)

  // Variables auxiliares para la UI
  const allGamesCount = 10;
  const allGamesCompleted = completedGames.length >= allGamesCount;
  const hasCv = Boolean(personal.cvFile);

  useEffect(() => {
    if (id && !currentGame) {
      startGame(id)
    }
  }, [id, currentGame, startGame])

  useEffect(() => {
    const hasContactData = Boolean(personal?.firstName && personal?.lastName);
    const hasPreferences = personal?.jobPreferences && (
      typeof personal.jobPreferences === 'string'
        ? personal.jobPreferences.trim() !== ''
        : personal.jobPreferences?.areas && personal.jobPreferences?.areas?.length > 0
    );
    const hasPersonalData = hasContactData && (hasPreferences || personal.completed);

    if (!hasPersonalData) {
      navigate('/register/contact');
    }
  }, [personal, navigate]);

  const handleSceneComplete = (log: GameLog) => {
    completeScene(log)
  }

  const handleNextScene = (sceneId: string) => {
    goToScene(sceneId)
  }

  // Detectar si es la primera escena
  const isFirstScene = currentGame && currentScene && currentGame.scenes[0]?.id === currentScene.id;

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

  // El juego ha terminado (no quedan escenas): volver automáticamente al menú,
  // salvo que toque mostrar el aviso de "falta adjuntar CV".
  useEffect(() => {
    if (currentGame && !currentScene && !(allGamesCompleted && !hasCv)) {
      navigate('/games');
    }
  }, [currentGame, currentScene, allGamesCompleted, hasCv, navigate]);

  if (!currentScene) {
    if (allGamesCompleted && !hasCv) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">¡Falta adjuntar el CV!</h2>
  
            <p className="mb-4">
              Has completado todos los minijuegos. Para generar el informe de empleabilidad, necesitas adjuntar tu CV.
            </p>
  
            <button
              onClick={() => navigate('/upload-cv')}
              className="px-6 py-3 bg-[#374ba6] text-white rounded-lg hover:bg-[#2d3f96]"
            >
              Ir a adjuntar CV
            </button>
          </div>
        </div>
      );
    }
  
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 transition-colors">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header del juego */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <span className="text-4xl mr-4">{currentGame.icon}</span>
            <div>
              <h1 className="text-3xl font-bold dark:text-gray-100" style={{ color: currentGame.color }}>
                {currentGame.title}
              </h1>
              <p className="text-lg text-gray-600 dark:text-gray-300">{currentGame.subtitle}</p>
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

          {/* Información general solo en la PRIMERA escena */}
          {isFirstScene && (
            <div className="bg-white dark:bg-slate-800 rounded-lg p-4 shadow-sm transition-colors">
              <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                <strong>Día:</strong> {currentGame.day} | <strong>Escenario:</strong> {currentGame.scenario}
              </p>
              <p className="text-gray-700 dark:text-gray-200">{currentGame.description}</p>
            </div>
          )}
        </div>

        {/* Escena actual */}
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg overflow-hidden transition-colors">
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
            className="px-4 py-2 text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-gray-100"
          >
            ← Volver al menú
          </button>
        </div>
      </div>
    </div>
  )
}

export default GameScenePage
