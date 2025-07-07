// nuevo-frontend/src/features/games/useGameController.ts

import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Game, GameScene, GameLog, SoftSkill } from '../../types/game';
import { games, getGameById } from '../../data/games';
import { RootState } from '../../app/store';
import { updateGameProgress, addGameLog, completeGame } from './gameSlice';

export const useGameController = () => {
  const dispatch = useDispatch();
  const gameState = useSelector((state: RootState) => state.game);
  const accessibility = useSelector((state: RootState) => state.accessibility);

  // currentGame y currentScene ahora se obtienen de Redux
  const currentGame = gameState.currentGameId ? getGameById(gameState.currentGameId) : null;
  const currentSceneIndex = gameState.currentGameId && currentGame ? (gameState.gameLogs[currentGame.id]?.length || 0) : 0;
  const currentScene = currentGame && currentSceneIndex < currentGame.scenes.length ? currentGame.scenes[currentSceneIndex] : null;
  const gameLogs = currentGame ? (gameState.gameLogs[currentGame.id] || []) : [];

  // Inicializar un juego
  const startGame = useCallback((gameId: string) => {
    const game = getGameById(gameId);
    if (game) {
      dispatch(updateGameProgress({ currentGameId: gameId }));
    }
  }, [dispatch]);

  // Completar una escena
  const completeScene = useCallback((log: GameLog) => {
    if (!currentGame) return;
    dispatch(addGameLog({ gameId: currentGame.id, log }));
    // Si es la última escena, completar el juego
    if (currentSceneIndex >= currentGame.scenes.length - 1) {
      handleCompleteGame();
    }
  }, [currentGame, currentSceneIndex, dispatch]);

  // Ir a una escena específica
  const goToScene = useCallback((sceneId: string) => {
    // No es necesario con el nuevo enfoque, ya que el avance es secuencial
  }, []);

  // Completar el juego actual
  const handleCompleteGame = useCallback(() => {
    if (!currentGame) return;
    // Calcular puntuación del juego
    const totalScore = gameLogs.reduce((sum, log) => {
      const scene = currentGame.scenes.find(s => s.id === log.sceneId);
      if (scene?.options) {
        const option = scene.options.find(o => o.id === log.selectedOptionId);
        return sum + (option?.score || 0);
      }
      return sum;
    }, 0);
    const averageScore = gameLogs.length > 0 ? totalScore / gameLogs.length : 0;
    // Crear la habilidad blanda evaluada
    const softSkill: SoftSkill = {
      id: currentGame.id,
      name: currentGame.softSkill,
      description: currentGame.description,
      icon: currentGame.icon,
      color: currentGame.color,
      gameId: currentGame.id,
      level: averageScore < 50 ? 'bajo' : averageScore < 75 ? 'medio' : 'alto',
      score: averageScore,
      confidence: 0.8,
      logs: gameLogs
    };
    dispatch(completeGame({ 
      gameId: currentGame.id,
      score: averageScore,
      softSkill 
    }));
  }, [currentGame, gameLogs, dispatch]);

  // Obtener progreso del juego
  const getGameProgress = useCallback(() => {
    if (!currentGame) return { current: 0, total: 0, percentage: 0 };
    return {
      current: currentSceneIndex + 1,
      total: currentGame.scenes.length,
      percentage: ((currentSceneIndex + 1) / currentGame.scenes.length) * 100
    };
  }, [currentGame, currentSceneIndex]);

  // Obtener siguiente juego disponible
  const getNextAvailableGame = useCallback(() => {
    if (!currentGame) return null;
    const currentIndex = games.findIndex(game => game.id === currentGame.id);
    if (currentIndex === -1 || currentIndex >= games.length - 1) {
      return null;
    }
    return games[currentIndex + 1];
  }, [currentGame]);

  // Verificar si un juego está disponible
  const isGameAvailable = useCallback((gameId: string) => {
    const gameIndex = games.findIndex(game => game.id === gameId);
    if (gameIndex === 0) return true;
    const previousGame = games[gameIndex - 1];
    const completedGames = gameState?.completedGames || [];
    return completedGames.includes(previousGame.id);
  }, [gameState?.completedGames]);

  return {
    currentGame,
    currentScene,
    gameProgress: getGameProgress(),
    gameLogs,
    accessibility,
    startGame,
    completeScene,
    goToScene,
    completeGame: handleCompleteGame,
    getNextAvailableGame,
    isGameAvailable,
    allGames: games,
    getGameById
  };
};