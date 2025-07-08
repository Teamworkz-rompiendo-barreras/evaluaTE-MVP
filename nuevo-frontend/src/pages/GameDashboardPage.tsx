// src/pages/GameDashboardPage.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { games } from '../data/games';
import GameCard from '../components/GameCard';
import { useAppSelector, useAppDispatch } from '../app/hooks';
import { useGameController } from '../features/games/useGameController';
import { clearCurrentGame } from '../features/games/gameSlice';

const GameDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const game = useAppSelector((state) => state.game);
  const { isGameAvailable } = useGameController();
  const dispatch = useAppDispatch();

  // Eliminar o comentar los console.log
  // console.log('GameDashboardPage - Renderizando versión con games importado');
  // console.log('GameDashboardPage - Total de juegos:', games.length);
  // console.log('GameDashboardPage - Componente montado correctamente');

  // Accesibilidad (puedes adaptar según tu lógica real)
  const accessibility = {
    contrastLevel: 'normal' as const,
    fontScale: 100,
    audioEnabled: true,
    visualHelp: false,
    timeExtensions: false,
  };

  // Lógica real de desbloqueo y completado
  const isUnlocked = (gameId: string, idx: number) => {
    if (idx === 0) return true;
    return isGameAvailable(gameId);
  };
  const isCompleted = (gameId: string) => game.completedGames.includes(gameId);
  const isCurrent = (gameId: string, idx: number) => {
    // El primer juego no completado y desbloqueado es el actual
    if (!isCompleted(gameId) && isUnlocked(gameId, idx)) return true;
    return false;
  };

  // El botón de resultados solo está activo si todos los juegos están completados
  const allCompleted = game.completedGames.length === games.length;

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
          <p>✅ Juegos completados: {game.completedGames.length}</p>
        </div>

        {/* Grid de minijuegos - DINÁMICO */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {games.map((g, idx) => (
            <GameCard
              key={g.id}
              game={g}
              isUnlocked={isUnlocked(g.id, idx)}
              isCurrent={isCurrent(g.id, idx)}
              isCompleted={isCompleted(g.id)}
              accessibility={accessibility}
              onClick={() => {
                if (isUnlocked(g.id, idx)) {
                  dispatch(clearCurrentGame());
                  navigate(`/games/${g.id}`);
                }
              }}
            />
          ))}
        </div>

        {/* Botón de prueba para Sentry */}
        <div className="flex justify-center my-6">
          <button
            onClick={() => { throw new Error('¡Esto es una prueba de Sentry!'); }}
            className="px-4 py-2 bg-red-600 text-white rounded shadow hover:bg-red-700"
          >
            Probar Sentry (lanzar error)
          </button>
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
            onClick={() => allCompleted && navigate('/resultados')}
            className={`px-6 py-3 rounded-lg transition-colors text-white ${allCompleted ? 'bg-green-500 hover:bg-green-600' : 'bg-gray-300 cursor-not-allowed'}`}
            disabled={!allCompleted}
          >
            Ver Resultados →
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameDashboardPage;