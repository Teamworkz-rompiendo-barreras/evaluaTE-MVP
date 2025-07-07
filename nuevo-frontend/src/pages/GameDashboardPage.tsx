// src/pages/GameDashboardPage.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { games } from '../data/games';
import GameCard from '../components/GameCard';

const GameDashboardPage: React.FC = () => {
  const navigate = useNavigate();

  console.log('GameDashboardPage - Renderizando versión con games importado');
  console.log('GameDashboardPage - Total de juegos:', games.length);
  console.log('GameDashboardPage - Componente montado correctamente');

  // Simulación de estado de desbloqueo y accesibilidad (ajustar según tu lógica real)
  const accessibility = {
    contrastLevel: 'normal' as const,
    fontScale: 100,
    audioEnabled: true,
    visualHelp: false,
    timeExtensions: false,
  };

  // Simulación: desbloquear todos los juegos para la demo
  const isUnlocked = (index: number) => true;
  const isCurrent = (index: number) => false;

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

        {/* Grid de minijuegos - DINÁMICO */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {games.map((game, idx) => (
            <GameCard
              key={game.id}
              game={game}
              isUnlocked={isUnlocked(idx)}
              isCurrent={isCurrent(idx)}
              accessibility={accessibility}
              onClick={() => navigate(`/games/${game.id}`)}
            />
          ))}
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
  );
};

export default GameDashboardPage;