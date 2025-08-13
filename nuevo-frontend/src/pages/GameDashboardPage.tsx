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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 transition-colors">
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

        {/* Contexto general de los minijuegos */}
        <div className="bg-blue-50 p-4 rounded-lg mb-8 no-max-width">
          <h2 className="font-bold text-xl mb-2">¡Bienvenido/a al reto de habilidades blandas!</h2>
          <p className="text-gray-700">
            Aquí podrás poner a prueba y desarrollar tus habilidades clave para el mundo laboral a través de 10 minijuegos interactivos. Cada día te enfrentarás a una situación diferente, donde no hay respuestas incorrectas: solo formas distintas de afrontar los retos del trabajo. ¡Juega, aprende y descubre tu potencial!
          </p>
        </div>

        {/* Grid de minijuegos - DINÁMICO */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {(Array.isArray(games) ? games : []).map((g, idx) => (
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
            Ir a adjuntar currículum →
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameDashboardPage;