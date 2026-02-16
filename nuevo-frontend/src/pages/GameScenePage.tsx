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
  // Eliminar o comentar los console.log
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  // Eliminar o comentar los console.log
  // console.log('GameScenePage - id del minijuego:', id);
  // console.log('GameScenePage - ruta actual:', window.location.pathname);

  // Estado del juego
  const { currentGame, currentScene, gameProgress } = useGameController()

  // Estado de accesibilidad
  const accessibility = useSelector((state: RootState) => state.accessibility)
  const completedGames = useSelector((state: RootState) => state.game.completedGames)

  // Variables auxiliares para la UI
  const allGamesCount = 10; // Total de juegos
  const allGamesCompleted = completedGames.length >= allGamesCount;
  const hasCv = Boolean(useSelector((state: RootState) => state.personal.cvFile));

  // Estado de personal
  const personal = useSelector((state: RootState) => state.personal)

  const {
    startGame,
    completeScene,
    goToScene
  } = useGameController()

  useEffect(() => {
    if (id && !currentGame) {
      startGame(id)
    }
  }, [id, currentGame, startGame])

  useEffect(() => {
    // Eliminar o comentar los console.log
    // console.log('🎮 GameScenePage - INICIO VALIDACIÓN');
    // console.log('🎮 GameScenePage - Estado personal:', personal);
    // console.log('🎮 GameScenePage - personal.completed:', personal.completed);

    // Verificar si los datos de contacto están completos
    const hasContactData = Boolean(personal?.firstName && personal?.lastName);

    // Verificar si las preferencias están completas
    const hasPreferences = personal?.jobPreferences && (
      typeof personal.jobPreferences === 'string'
        ? personal.jobPreferences.trim() !== ''
        : personal.jobPreferences?.areas && personal.jobPreferences?.areas?.length > 0
    );

    // Los datos personales están completamente completos cuando se tienen tanto contact como preferences
    const hasPersonalData = hasContactData && (hasPreferences || personal.completed);

    // Eliminar o comentar los console.log
    // console.log('🎮 GameScenePage - hasContactData:', hasContactData);
    // console.log('🎮 GameScenePage - hasPreferences:', hasPreferences);
    // console.log('🎮 GameScenePage - hasPersonalData:', hasPersonalData);

    if (!hasPersonalData) {
      // Eliminar o comentar los console.log
      // console.log('🎮 GameScenePage - REDIRIGIENDO a /register/contact - datos personales no completados');
      navigate('/register/contact');
      return;
    }

    // Eliminar o comentar los console.log
    // console.log('🎮 GameScenePage - ✅ Validaciones pasadas, continuando...');
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

  if (!currentScene) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">¡Juego completado!</h2>
          <p className="mb-4">Has terminado {currentGame.title}</p>
          <button
            onClick={() => navigate('/games')}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 mr-4"
          >
            Volver al menú
          </button>

          {/* Solo mostrar si TODOS los juegos están completados Y hay CV */}
          {allGamesCompleted && hasCv && (
            <button
              onClick={() => navigate('/resultados')}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Ver Informe de Empleabilidad
            </button>
          )}

          {/* Si todos los juegos están completados pero NO hay CV, llevar a subir CV */}
          {allGamesCompleted && !hasCv && (
            <button
              onClick={() => navigate('/upload-cv')}
              className="px-6 py-3 bg-[#374ba6] text-white rounded-lg hover:bg-[#2d3f96]"
            >
              Ir a adjuntar CV
            </button>
          )}
        </div>
      </div>
    )
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