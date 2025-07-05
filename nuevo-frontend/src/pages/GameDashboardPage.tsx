// src/pages/GameDashboardPage.tsx
import React from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { games } from '../data/games';
import { RootState } from '../app/store';
import GameCard from '../components/GameCard';

const GameDashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const completedGames = useSelector((state: RootState) => state.game.completedGames)
  const accessibility = useSelector((state: RootState) => state.accessibility)

  const handleGameClick = (gameId: string) => {
    navigate(`/game/${gameId}`)
  }

  const isGameAvailable = (gameId: string) => {
    const gameIndex = games.findIndex(game => game.id === gameId)
    if (gameIndex === 0) return true // El primer juego siempre está disponible
    
    const previousGame = games[gameIndex - 1]
    return completedGames.includes(previousGame.id)
  }

  const getProgressPercentage = () => {
    return (completedGames.length / games.length) * 100
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            🎮 EvalúaTE - Minijuegos
          </h1>
          <p className="text-lg text-gray-600 mb-6">
            Evalúa tus 10 habilidades blandas clave a través de minijuegos interactivos
          </p>
          
          {/* Progreso general */}
          <div className="bg-white rounded-lg p-6 shadow-sm mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Progreso General</h2>
              <span className="text-2xl font-bold text-blue-600">
                {completedGames.length}/{games.length}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${getProgressPercentage()}%` }}
              />
            </div>
            <p className="text-sm text-gray-600 mt-2">
              {getProgressPercentage().toFixed(0)}% completado
            </p>
          </div>
        </div>

        {/* Grid de minijuegos */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {games.map((game, index) => {
            const isCompleted = completedGames.includes(game.id)
            const isAvailable = isGameAvailable(game.id)
            
            return (
              <GameCard
                key={game.id}
                game={game}
                isUnlocked={isCompleted}
                isCurrent={index === completedGames.length}
                onClick={() => isAvailable && handleGameClick(game.id)}
                accessibility={{
                  contrastLevel: accessibility.contrastLevel === 'alto' || accessibility.contrastLevel === 'muy-alto' ? 'high' : 'normal',
                  fontScale: accessibility.fontScale,
                  audioEnabled: accessibility.audioAssistiveMode,
                  visualHelp: accessibility.showPictograms,
                  timeExtensions: true
                }}
              />
            )
          })}
        </div>

        {/* Información adicional */}
        <div className="mt-12 bg-white rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">¿Cómo funcionan los minijuegos?</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl mb-2">🎯</div>
              <h4 className="font-semibold mb-2">Evaluación Invisible</h4>
              <p className="text-sm text-gray-600">
                No hay respuestas correctas o incorrectas. Solo actúa como lo harías en la vida real.
              </p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">🧠</div>
              <h4 className="font-semibold mb-2">Habilidades Blandas</h4>
              <p className="text-sm text-gray-600">
                Cada minijuego evalúa una habilidad específica del informe WEF 2025.
              </p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">📊</div>
              <h4 className="font-semibold mb-2">Análisis Inteligente</h4>
              <p className="text-sm text-gray-600">
                Tu comportamiento se analiza para generar un informe personalizado.
              </p>
            </div>
          </div>
        </div>

        {/* Botones de acción */}
        <div className="mt-8 flex justify-center space-x-4">
          <button
            onClick={() => navigate('/register/contact')}
            className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            ← Datos Personales
          </button>
          <button
            onClick={() => {
              console.log('DEBUG - Estado completo:', {
                personal: useSelector((state: RootState) => state.personal),
                game: useSelector((state: RootState) => state.game),
                progress: useSelector((state: RootState) => state.progress)
              });
            }}
            className="px-6 py-3 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
          >
            Debug Estado
          </button>
          <button
            onClick={() => navigate('/resultados')}
            className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            Ver Resultados →
          </button>
        </div>
      </div>
    </div>
  )
}

export default GameDashboardPage