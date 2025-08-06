// Script para corregir el problema del bucle infinito en minijuegos
// Este archivo contiene las correcciones necesarias para todos los minijuegos

export interface Scene {
  id: string;
  title: string;
  description: string;
  type: string;
  options: Array<Record<string, unknown>>;
  nextSceneId?: string;
}

export interface Game {
  scenes: Scene[];
  [key: string]: unknown;
}

export const fixGameScenes = (games: Game[]): Game[] => {
  return (Array.isArray(games) ? games : []).map((game: Game) => {
    // Buscar la escena feedback-final
    const feedbackFinalIndex = game.scenes.findIndex((scene: Scene) => scene.id === 'feedback-final');
    
    if (feedbackFinalIndex !== -1) {
      // Agregar nextSceneId a feedback-final
      game.scenes[feedbackFinalIndex].nextSceneId = 'game-complete';
      
      // Agregar escena game-complete al final
      game.scenes.push({
        id: 'game-complete',
        title: 'Minijuego Completado',
        description: 'Has completado exitosamente el minijuego.',
        type: 'choice',
        options: [
          { id: 'volver-menu', text: 'Volver al menú', score: 0 }
        ]
      });
    }
    return game;
  });
}; 