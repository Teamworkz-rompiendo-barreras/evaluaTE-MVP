// nuevo-frontend/src/features/games/useGameController.ts

import { useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Game, GameScene, GameLog, SoftSkill } from '../../types/game';
import { games, getGameById } from '../../data/games';
import { RootState } from '../../app/store';
import { updateGameProgress, addGameLog, completeGame } from './gameSlice';

export const useGameController = () => {
  const dispatch = useDispatch();
  const gameState = useSelector((state: RootState) => state.game);
  const accessibility = useSelector((state: RootState) => state.accessibility);

  const [currentGame, setCurrentGame] = useState<Game | null>(null);
  const [currentSceneIndex, setCurrentSceneIndex] = useState(0);
  const [gameLogs, setGameLogs] = useState<GameLog[]>([]);

  // Inicializar un juego
  const startGame = useCallback((gameId: string) => {
    const game = getGameById(gameId);
    if (game) {
      setCurrentGame(game);
      setCurrentSceneIndex(0);
      setGameLogs([]);
      dispatch(updateGameProgress({ currentGameId: gameId }));
    }
  }, [dispatch]);

  // Obtener la escena actual
  const getCurrentScene = useCallback((): GameScene | null => {
    if (!currentGame || currentSceneIndex >= currentGame.scenes.length) {
      return null;
    }
    return currentGame.scenes[currentSceneIndex];
  }, [currentGame, currentSceneIndex]);

  // Completar una escena
  const completeScene = useCallback((log: GameLog) => {
    setGameLogs(prev => [...prev, log]);
    
    // Guardar el log en el estado global
    dispatch(addGameLog({ gameId: currentGame?.id || '', log }));

    // Verificar si es la última escena
    if (currentGame && currentSceneIndex >= currentGame.scenes.length - 1) {
      handleCompleteGame();
    } else {
      setCurrentSceneIndex(prev => prev + 1);
    }
  }, [currentGame, currentSceneIndex, dispatch]);

  // Ir a una escena específica
  const goToScene = useCallback((sceneId: string) => {
    if (!currentGame) return;
    
    const sceneIndex = currentGame.scenes.findIndex(scene => scene.id === sceneId);
    if (sceneIndex !== -1) {
      setCurrentSceneIndex(sceneIndex);
    }
  }, [currentGame]);

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

    const averageScore = totalScore / gameLogs.length;

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
      confidence: 0.8, // Se puede calcular basado en consistencia
      logs: gameLogs
    };

    // Guardar en el estado global
    dispatch(completeGame({ 
      gameId: currentGame.id, 
      score: averageScore,
      softSkill 
    }));

    // Limpiar estado local
    setCurrentGame(null);
    setCurrentSceneIndex(0);
    setGameLogs([]);
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
    // Verificar que gameState existe y tiene la propiedad completedGames
    const completedGames = gameState?.completedGames || [];
    const currentIndex = games.findIndex(game => game.id === currentGame?.id);
    
    if (currentIndex === -1 || currentIndex >= games.length - 1) {
      return null;
    }
    
    return games[currentIndex + 1];
  }, [currentGame, gameState?.completedGames]);

  // Verificar si un juego está disponible
  const isGameAvailable = useCallback((gameId: string) => {
    const gameIndex = games.findIndex(game => game.id === gameId);
    if (gameIndex === 0) return true; // El primer juego siempre está disponible
    
    const previousGame = games[gameIndex - 1];
    const completedGames = gameState?.completedGames || [];
    return completedGames.includes(previousGame.id);
  }, [gameState?.completedGames]);

  return {
    // Estado
    currentGame,
    currentScene: getCurrentScene(),
    gameProgress: getGameProgress(),
    gameLogs,
    accessibility,
    
    // Acciones
    startGame,
    completeScene,
    goToScene,
    completeGame: handleCompleteGame,
    getNextAvailableGame,
    isGameAvailable,
    
    // Utilidades
    allGames: games,
    getGameById
  };
};