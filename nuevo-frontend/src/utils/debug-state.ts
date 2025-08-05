/**
 * Utilidad para debuggear el estado de Redux
 */

export const debugState = (state: any, label: string = 'Estado') => {
  console.log(`🔍 DEBUG - ${label}:`);
  console.log('  • Estado completo:', state);
  
  if (state.personal) {
    console.log('  • personal.softSkills:', state.personal.softSkills);
    console.log('  • personal.softSkills.length:', state.personal.softSkills?.length);
    console.log('  • personal.report:', state.personal.report);
    console.log('  • personal.report?.softSkills:', state.personal.report?.softSkills);
    console.log('  • personal.report?.softSkills.length:', state.personal.report?.softSkills?.length);
  }
  
  if (state.game) {
    console.log('  • game.completedGames:', state.game.completedGames);
  }
};

export const validateSoftSkills = (softSkills: any[]): boolean => {
  if (!softSkills || !Array.isArray(softSkills)) {
    console.log('❌ softSkills no es un array:', softSkills);
    return false;
  }
  
  if (softSkills.length === 0) {
    console.log('❌ softSkills está vacío');
    return false;
  }
  
  const validSkills = softSkills.every(skill => 
    skill && 
    typeof skill.skill === 'string' && 
    typeof skill.score === 'number' && 
    typeof skill.level === 'string'
  );
  
  if (!validSkills) {
    console.log('❌ softSkills tiene elementos inválidos:', softSkills);
    return false;
  }
  
  console.log('✅ softSkills es válido:', softSkills);
  return true;
}; 