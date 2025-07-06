// src/pages/GameDashboardPage.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { games } from '../data/games';

const GameDashboardPage: React.FC = () => {
  const navigate = useNavigate()

  console.log('GameDashboardPage - Renderizando versión con games importado')
  console.log('GameDashboardPage - Total de juegos:', games.length)
  console.log('GameDashboardPage - Componente montado correctamente')

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
        </div>

        {/* Debug info */}
        <div className="bg-yellow-100 p-4 rounded-lg mb-8">
          <h3 className="font-semibold mb-2">Debug Info:</h3>
          <p>✅ Componente GameDashboardPage cargado correctamente</p>
          <p>✅ Games importado: {games.length} juegos disponibles</p>
          <p>✅ Primer juego: {games[0]?.title}</p>
        </div>

        {/* Grid de minijuegos - VERSIÓN ESTÁTICA */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {/* Tarjeta estática 1 */}
          <div className="game-card bg-white border-2 border-gray-300 p-4 rounded-lg cursor-pointer hover:border-blue-400 hover:shadow-lg">
            <div className="text-center mb-3">
              <div className="text-4xl mb-2" style={{ color: '#F2D680' }}>
                📞
              </div>
            </div>
            <div className="text-center">
              <h3 className="font-semibold text-sm mb-1">
                Primera llamada del día
              </h3>
              <p className="text-xs text-gray-600 mb-2">
                Toma de decisiones
              </p>
              <p className="text-xs text-gray-500 mb-2">
                Lunes
              </p>
              <span className="text-xs px-2 py-1 rounded-full bg-blue-200 text-blue-700">
                Disponible
              </span>
            </div>
          </div>

          {/* Tarjeta estática 2 */}
          <div className="game-card bg-white border-2 border-gray-300 p-4 rounded-lg cursor-pointer hover:border-blue-400 hover:shadow-lg">
            <div className="text-center mb-3">
              <div className="text-4xl mb-2" style={{ color: '#374BA6' }}>
                🧩
              </div>
            </div>
            <div className="text-center">
              <h3 className="font-semibold text-sm mb-1">
                Algo no cuadra
              </h3>
              <p className="text-xs text-gray-600 mb-2">
                Resolución de problemas
              </p>
              <p className="text-xs text-gray-500 mb-2">
                Martes
              </p>
              <span className="text-xs px-2 py-1 rounded-full bg-blue-200 text-blue-700">
                Disponible
              </span>
            </div>
          </div>

          {/* Tarjeta estática 3 */}
          <div className="game-card bg-white border-2 border-gray-300 p-4 rounded-lg cursor-pointer hover:border-blue-400 hover:shadow-lg">
            <div className="text-center mb-3">
              <div className="text-4xl mb-2" style={{ color: '#FF6B6B' }}>
                🤝
              </div>
            </div>
            <div className="text-center">
              <h3 className="font-semibold text-sm mb-1">
                Trabajo en equipo
              </h3>
              <p className="text-xs text-gray-600 mb-2">
                Colaboración
              </p>
              <p className="text-xs text-gray-500 mb-2">
                Miércoles
              </p>
              <span className="text-xs px-2 py-1 rounded-full bg-blue-200 text-blue-700">
                Disponible
              </span>
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