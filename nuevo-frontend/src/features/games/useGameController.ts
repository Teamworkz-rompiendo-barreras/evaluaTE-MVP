// src/features/games/useGameController.ts
import { useCallback, useMemo, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { GameLog, SoftSkill } from '../../types/game';
import { games, getGameById } from '../../data/games';
import { RootState } from '../../app/store';
import { updateGameProgress, addGameLog, completeGame, resetGameLogs } from './gameSlice';

export const useGameController = () => {
  const dispatch = useDispatch();
  const gameState = useSelector((state: RootState) => state.game);
  const accessibility = useSelector((state: RootState) => state.accessibility);

  const currentGame = gameState.currentGameId ? getGameById(gameState.currentGameId) : null;
  const currentSceneIndex = gameState.currentGameId && currentGame ? (gameState.gameLogs[currentGame.id]?.length || 0) : 0;
  const currentScene = currentGame && currentSceneIndex < currentGame.scenes.length ? currentGame.scenes[currentSceneIndex] : null;

  const gameLogs = useMemo(() => currentGame ? (gameState.gameLogs[currentGame.id] || []) : [], [currentGame, gameState.gameLogs]);

  const startTimeRef = useRef<number>(performance.now());

  useEffect(() => {
    startTimeRef.current = performance.now();
  }, [currentSceneIndex]);

  const startGame = useCallback((gameId: string) => {
    const game = getGameById(gameId);
    if (game) {
      if (!gameState.completedGames.includes(gameId)) {
        dispatch(resetGameLogs(gameId));
      }
      dispatch(updateGameProgress({ currentGameId: gameId }));
      startTimeRef.current = performance.now();
    }
  }, [dispatch, gameState.completedGames]);

  const completeScene = useCallback((selectedOptionId: string) => {
    if (!currentGame || !currentScene) return;

    const reactionTimeMs = Math.round(performance.now() - startTimeRef.current);

    const log: GameLog = {
      sceneId: currentScene.id,
      selectedOptionId,
      reactionTimeMs,
      timestamp: new Date().toISOString()
    };

    dispatch(addGameLog({ gameId: currentGame.id, log }));

    const isLastScene = 
      currentGame.scenes[currentSceneIndex + 1]?.id === 'game-complete' || 
      (currentSceneIndex + 1 >= currentGame.scenes.length);

    if (isLastScene) {
      // CÁLCULO REAL DE LA PUNTUACIÓN DE LA PARTIDA
      const allLogs = [...gameLogs, log];
      let totalScore = 0;
      let validOptionsCount = 0;

      allLogs.forEach(l => {
        const scene = currentGame.scenes.find(s => s.id === l.sceneId);
        if (scene && scene.options) {
          const option = scene.options.find(o => o.id === l.selectedOptionId);
          if (option && typeof option.score === 'number') {
            totalScore += option.score;
            validOptionsCount++;
          }
        }
      });

      // Sacamos la media exacta de todas las decisiones tomadas
      const finalScore = validOptionsCount > 0 ? Math.round(totalScore / validOptionsCount) : 0;
      
      // Ajustamos la etiqueta de nivel para enriquecer el contexto de la IA
      let finalLevel: 'bajo' | 'medio' | 'alto' = 'medio';
      if (finalScore >= 80) finalLevel = 'alto';
      else if (finalScore <= 40) finalLevel = 'bajo';

      const softSkillPlaceholder: SoftSkill = {
        id: currentGame.id,
        name: currentGame.softSkill,
        description: currentGame.description,
        icon: currentGame.icon,
        color: currentGame.color,
        gameId: currentGame.id,
        level: finalLevel, 
        score: finalScore, 
        confidence: 1,
        logs: allLogs
      };

      dispatch(completeGame({
        gameId: currentGame.id,
        score: finalScore,
        softSkill: softSkillPlaceholder
      }));
    }
  }, [currentGame, currentScene, currentSceneIndex, dispatch, gameLogs]);

  const goToScene = useCallback((_sceneId: string) => {}, []);

  const getGameProgress = useCallback(() => {
    if (!currentGame) return { current: 0, total: 0, percentage: 0 };
    return {
      current: currentSceneIndex + 1,
      total: currentGame.scenes.length,
      percentage: ((currentSceneIndex + 1) / currentGame.scenes.length) * 100
    };
  }, [currentGame, currentSceneIndex]);

  const isGameAvailable = useCallback((gameId: string) => {
    const gameIndex = games.findIndex(g => g.id === gameId);
    if (gameIndex === 0) return true;
    const previousGame = games[gameIndex - 1];
    if (!previousGame) return false;
    return (gameState?.completedGames || []).includes(previousGame.id);
  }, [gameState?.completedGames]);

  const getNextAvailableGame = useCallback(() => {
    if (!currentGame) return null;
    const currentIndex = games.findIndex(g => g.id === currentGame.id);
    if (currentIndex === -1 || currentIndex >= games.length - 1) return null;
    return games[currentIndex + 1];
  }, [currentGame]);

  return {
    currentGame,
    currentScene,
    gameProgress: getGameProgress(),
    gameLogs,
    accessibility,
    startGame,
    completeScene,
    goToScene,
    completeGame: () => {}, 
    getNextAvailableGame,
    isGameAvailable,
    allGames: games,
    getGameById
  };
};