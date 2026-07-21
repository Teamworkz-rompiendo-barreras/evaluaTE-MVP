// src/pages/GameDashboardPage.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { games } from '../data/games';
import GameCard from '../components/GameCard';
import { useAppSelector } from '../app/hooks';
import { useGameController } from '../features/games/useGameController';

const GameDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const game = useAppSelector((state) => state.game);
  
  // CORRECCIÓN: Importamos startGame para gestionar la entrada al juego
  const { isGameAvailable, startGame } = useGameController();

  const accessibility = {
    contrastLevel: 'normal' as const,
    fontScale: 100,
    audioEnabled: true,
    visualHelp: false,
    timeExtensions: false,
  };

  const isUnlocked = (gameId: string, idx: number) => {
    if (idx === 0) return true;
    return isGameAvailable(gameId);
  };
  
  const isCompleted = (gameId: string) => game.completedGames.includes(gameId);
  
  const isCurrent = (gameId: string, idx: number) => {
    if (!isCompleted(gameId) && isUnlocked(gameId, idx)) return true;
    return false;
  };

  const allCompleted = game.completedGames.length === games.length;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 transition-colors">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 dark:text-gray-100 mb-4">
            🎮 EvalúaTE - Minijuegos
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
            Evalúa tus 10 habilidades blandas clave a través de minijuegos interactivos
          </p>
        </div>

        <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg mb-8 no-max-width">
          <h2 className="font-bold text-xl mb-2 dark:text-gray-100">¡Bienvenido/a al reto de habilidades blandas!</h2>
          <p className="text-gray-700 dark:text-gray-200">
            Aquí podrás poner a prueba y desarrollar tus habilidades clave para el mundo laboral a través de 10 minijuegos interactivos. Cada día te enfrentarás a una situación diferente, donde no hay respuestas incorrectas: solo formas distintas de afrontar los retos del trabajo. ¡Juega, aprende y descubre tu potencial!
          </p>
        </div>

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
                  // Ejecutamos startGame en lugar de inyectar Redux a lo bruto
                  startGame(g.id);
                  navigate(`/games/${g.id}`);
                }
              }}
            />
          ))}
        </div>

        <div className="mt-8 flex flex-col sm:flex-row justify-center items-center gap-4">
          <button
            type="button"
            onClick={() => navigate('/register/contact')}
            className="px-6 py-3 w-full sm:w-auto bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors focus:ring-4 focus:ring-gray-300 outline-none"
          >
            ← Datos Personales
          </button>
          
          <button
            type="button"
            onClick={() => {
              if (allCompleted) navigate('/upload-cv');
            }}
            aria-disabled={!allCompleted ? "true" : "false"}
            aria-describedby={!allCompleted ? "motivo-bloqueo" : undefined}
            className={`px-6 py-3 w-full sm:w-auto rounded-lg transition-colors font-semibold focus:outline-none focus:ring-4 focus:ring-blue-300 ${
              allCompleted
                ? 'bg-[#374ba6] text-white shadow-md hover:bg-[#2d3f96] hover:shadow-lg'
                : 'bg-gray-300 text-gray-600 cursor-not-allowed dark:bg-gray-700 dark:text-gray-400'
            }`}
          >
            Ir a adjuntar currículum →
          </button>

          {!allCompleted && (
            <span id="motivo-bloqueo" className="sr-only">
              Debes completar los {games.length} minijuegos antes de poder adjuntar tu currículum.
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default GameDashboardPage;