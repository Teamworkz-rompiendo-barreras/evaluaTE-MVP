// Script para corregir el problema del bucle infinito en minijuegos
// Este archivo contiene las correcciones necesarias para todos los minijuegos

export const fixGameScenes = (games: unknown[]): unknown[] => {
  return games.map((game: Record<string, unknown>) => {
    // Buscar la escena feedback-final
    const feedbackFinalIndex = (game.scenes as any[]).findIndex((scene: any) => scene.id === 'feedback-final');
    
    if (feedbackFinalIndex !== -1) {
      // Agregar nextSceneId a feedback-final
      (game.scenes as any[])[feedbackFinalIndex].nextSceneId = 'game-complete';
      
      // Agregar escena game-complete al final
      (game.scenes as any[]).push({
        id: 'game-complete',
        title: 'Minijuego Completado',
        description: `Has completado exitosamente el minijuego de ${game.softSkill}. ¡Bien hecho!`,
        type: 'choice',
        options: [
          { id: 'volver-menu', text: 'Volver al menú', score: 0 }
        ]
      });
    }
    
    return game;
  });
}; 