import React from 'react';
import { games } from '../data/games';

const SimpleDashboardPage: React.FC = () => {
  // console.log('SimpleDashboardPage - Renderizando con', games.length, 'juegos');

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            🎮 EvalúaTE - Minijuegos (SIMPLE)
          </h1>
          <p className="text-lg text-gray-600 mb-6">
            Dashboard simplificado para testing
          </p>
        </div>

        {/* Grid de minijuegos SIMPLE */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {games.map((game) => {
            // console.log('SimpleDashboardPage - Renderizando juego:', game.id, 'index:', index);
            
            return (
              <div
                key={game.id}
                className="game-card bg-white border-2 border-gray-300 p-4 rounded-lg cursor-pointer hover:border-blue-400 hover:shadow-lg"
                // onClick={() => console.log('Clic en juego:', game.id)}
              >
                {/* Icono del juego */}
                <div className="text-center mb-3">
                  <div className="text-4xl mb-2" style={{ color: game.color }}>
                    {game.icon}
                  </div>
                </div>

                {/* Información del juego */}
                <div className="text-center">
                  <h3 className="font-semibold text-sm mb-1">
                    {game.title}
                  </h3>
                  <p className="text-xs text-gray-600 mb-2">
                    {game.subtitle}
                  </p>
                  <p className="text-xs text-gray-500 mb-2">
                    {game.day}
                  </p>
                  <span className="text-xs px-2 py-1 rounded-full bg-blue-200 text-blue-700">
                    Disponible
                  </span>
                </div>
              </div>
            )
          })}
        </div>

        {/* Debug info */}
        <div className="mt-8 bg-yellow-100 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Debug Info:</h3>
          <p>Total de juegos: {games.length}</p>
          <p>Primer juego ID: {games[0]?.id}</p>
          <p>Primer juego título: {games[0]?.title}</p>
        </div>
      </div>
    </div>
  )
}

export default SimpleDashboardPage 