// Script para verificar y corregir la estructura de todos los minijuegos
import { games } from './games';

export const verifyAndFixGames = () => {
  const issues: string[] = [];
  
  games.forEach((game, _gameIndex) => {
    // console.log(`Verificando minijuego ${gameIndex + 1}: ${game.title}`);
    
    // Verificar que tenga escenas
    if (!game.scenes || game.scenes.length === 0) {
      issues.push(`${game.title}: No tiene escenas`);
      return;
    }
    
    // Verificar que la última escena sea game-complete
    const lastScene = game.scenes[game.scenes.length - 1];
    if (lastScene && lastScene.id !== 'game-complete') {
      issues.push(`${game.title}: No tiene escena game-complete al final`);
    }
    
    // Verificar que feedback-final tenga nextSceneId
    const feedbackFinal = game.scenes.find(scene => scene.id === 'feedback-final');
    if (feedbackFinal && !feedbackFinal.nextSceneId) {
      issues.push(`${game.title}: feedback-final no tiene nextSceneId`);
    }
    
    // Verificar que todas las escenas tengan nextSceneId excepto la última
    game.scenes.forEach((scene, sceneIndex) => {
      if (sceneIndex < game.scenes.length - 1 && !scene.nextSceneId) {
        issues.push(`${game.title} - ${scene.id}: No tiene nextSceneId`);
      }
    });
  });
  
  if (issues.length === 0) {
    // console.log('✅ Todos los minijuegos están correctamente estructurados');
  } else {
    // console.log('❌ Problemas encontrados:');
    // issues.forEach(issue => console.log(`  - ${issue}`));
  }
  
  return issues;
};

// Ejecutar verificación
if (typeof window !== 'undefined') {
  // Solo en el navegador
  (window as unknown as { verifyGames: unknown }).verifyGames = verifyAndFixGames;
} 