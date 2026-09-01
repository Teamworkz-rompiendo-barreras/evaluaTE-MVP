import React from 'react';
import { games } from '../data/games';

const SimpleDashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 transition-colors">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 dark:text-white mb-4">
            🎮 EvalúaTE - Minijuegos (SIMPLE)
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
            Dashboard simplificado para testing
          </p>
        </div>

        {/* Grid de minijuegos ACCESIBLE */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {(Array.isArray(games) ? games : []).map((game) => {
            return (
              <button
                key={game.id}
                className="game-card bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 p-4 rounded-lg cursor-pointer hover:border-blue-400 dark:hover:border-blue-400 hover:shadow-lg focus:outline-none focus:ring-4 focus:ring-blue-300 transition-all text-left w-full group"
                aria-label={`Acceder al minijuego ${game.title}: ${game.subtitle}`}
              >
                {/* Icono del juego */}
                <div className="text-center mb-3">
                  <div className="text-4xl mb-2 transition-transform group-hover:scale-110" style={{ color: game.color }} aria-hidden="true">
                    {game.icon}
                  </div>
                </div>

                {/* Información del juego */}
                <div className="text-center">
                  <h3 className="font-semibold text-sm mb-1 text-gray-900 dark:text-white">
                    {game.title}
                  </h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                    {game.subtitle}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mb-2">
                    {game.day}
                  </p>
                  <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    Disponible
                  </span>
                </div>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default SimpleDashboardPage;