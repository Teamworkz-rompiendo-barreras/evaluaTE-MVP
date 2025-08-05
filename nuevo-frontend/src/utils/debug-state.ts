/**
 * Utilidad para debuggear el estado de Redux
 */

export const debugState = (state: unknown) => {
  // console.log(`🔍 DEBUG - Estado:`);
  // console.log('  • Estado completo:', state);
  
  if (state && typeof state === 'object' && 'personal' in state) {
    // const personalState = (state as { personal: unknown }).personal;
    // console.log('  • personal.softSkills:', personalState?.softSkills);
    // console.log('  • personal.softSkills.length:', personalState?.softSkills?.length);
    // console.log('  • personal.report:', personalState?.report);
    // console.log('  • personal.report?.softSkills:', personalState?.report?.softSkills);
    // console.log('  • personal.report?.softSkills.length:', personalState?.report?.softSkills?.length);
  }
  
  if (state && typeof state === 'object' && 'game' in state) {
    // const gameState = (state as { game: unknown }).game;
    // console.log('  • game.completedGames:', gameState?.completedGames);
  }
};

import { validateSoftSkillsArray } from './data-validation';

export const validateSoftSkills = (softSkills: unknown[]): boolean => {
  return validateSoftSkillsArray(softSkills);
}; 