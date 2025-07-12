import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../app/store';
import { games } from '../data/games';

const GameDebug: React.FC = () => {
  const gameState = useSelector((state: RootState) => state.game);
  const personal = useSelector((state: RootState) => state.personal);

  const currentGame = gameState.currentGameId ? games.find(g => g.id === gameState.currentGameId) : null;
  const currentSceneIndex = gameState.currentGameId && currentGame ? (gameState.gameLogs[currentGame.id]?.length || 0) : 0;
  const currentScene = currentGame && currentSceneIndex < currentGame.scenes.length ? currentGame.scenes[currentSceneIndex] : null;

  return (
    <div className="fixed top-4 right-4 bg-yellow-100 border border-yellow-400 rounded-lg p-4 max-w-sm z-50">
      <h3 className="font-bold text-sm mb-2">🎮 Debug Minijuegos</h3>
      <div className="text-xs space-y-1">
        <div><strong>Juego actual:</strong> {currentGame?.title || 'Ninguno'}</div>
        <div><strong>Escena actual:</strong> {currentScene?.id || 'Ninguna'} ({currentSceneIndex + 1}/{currentGame?.scenes.length || 0})</div>
        <div><strong>Juegos completados:</strong> {gameState.completedGames.length}/10</div>
        <div><strong>Datos personales:</strong> {personal.completed ? '✅' : '❌'}</div>
        <div><strong>Logs del juego:</strong> {gameState.gameLogs[currentGame?.id || '']?.length || 0}</div>
        <div className="mt-2">
          <button
            onClick={() => {
              console.log('🎮 Debug - Estado completo:', { gameState, personal, currentGame, currentScene });
            }}
            className="bg-blue-500 text-white px-2 py-1 rounded text-xs"
          >
            Log Estado
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameDebug; 