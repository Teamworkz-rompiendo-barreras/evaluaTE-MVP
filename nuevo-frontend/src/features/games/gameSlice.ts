import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { GameLog, SoftSkill } from '../../types/game';

interface GameState {
  currentGameId: string | null;
  completedGames: string[];
  gameLogs: Record<string, GameLog[]>;
  softSkills: SoftSkill[];
  adaptations: string[];
}

const initialState: GameState = {
  currentGameId: null,
  completedGames: [],
  gameLogs: {},
  softSkills: [],
  adaptations: []
};

const gameSlice = createSlice({
  name: 'game',
  initialState,
  reducers: {
    updateGameProgress: (state, action: PayloadAction<{ currentGameId: string }>) => {
      state.currentGameId = action.payload.currentGameId;
    },

    addGameLog: (state, action: PayloadAction<{ gameId: string; log: GameLog }>) => {
      const { gameId, log } = action.payload;
      if (!state.gameLogs[gameId]) {
        state.gameLogs[gameId] = [];
      }
      state.gameLogs[gameId].push(log);
    },

    completeGame: (state, action: PayloadAction<{
      gameId: string;
      score: number;
      softSkill: SoftSkill
    }>) => {
      const { gameId, softSkill } = action.payload;

      // Marcar juego como completado
      if (!state.completedGames.includes(gameId)) {
        state.completedGames.push(gameId);
      }

      // Actualizar o agregar habilidad blanda
      const existingIndex = state.softSkills.findIndex(skill => skill.id === gameId);
      if (existingIndex >= 0) {
        state.softSkills[existingIndex] = softSkill;
      } else {
        state.softSkills.push(softSkill);
      }

      // Limpiar juego actual - ELIMINADO para evitar reset loop en GameScenePage
      // state.currentGameId = null;
    },

    addAdaptation: (state, action: PayloadAction<string>) => {
      if (!state.adaptations.includes(action.payload)) {
        state.adaptations.push(action.payload);
      }
    },

    resetGameState: (state) => {
      state.currentGameId = null;
      state.completedGames = [];
      state.gameLogs = {};
      state.softSkills = [];
      state.adaptations = [];
    },

    clearCurrentGame: (state) => {
      state.currentGameId = null;
    },

    resetGameLogs: (state, action: PayloadAction<string>) => {
      // Limpia los logs del juego indicado
      delete state.gameLogs[action.payload];
    }
  }
});

export const {
  updateGameProgress,
  addGameLog,
  completeGame,
  addAdaptation,
  resetGameState,
  clearCurrentGame,
  resetGameLogs
} = gameSlice.actions;

export default gameSlice.reducer; 