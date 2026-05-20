/**
 * Utilidades para validación de datos y prevención de errores
 */

/**
 * Valida si un valor es un array válido y no está vacío
 */
export const isValidArray = <T>(value: unknown): value is T[] => {
  return Array.isArray(value) && value.length > 0;
};

/**
 * Valida si un valor es un array válido (puede estar vacío)
 */
export const isArray = <T>(value: unknown): value is T[] => {
  return Array.isArray(value);
};

/**
 * Ejecuta map de forma segura en un array, retornando un array vacío si el valor no es válido
 */
export const safeMap = <T, R>(
  array: T[] | undefined | null,
  mapper: (item: T, index: number) => R
): R[] => {
  if (!isValidArray(array)) {
    return [];
  }
  return array.map(mapper);
};

/**
 * Ejecuta map de forma segura en un array, retornando un array vacío si el valor no es válido
 * Versión que acepta arrays vacíos
 */
export const safeMapAllowEmpty = <T, R>(
  array: T[] | undefined | null,
  mapper: (item: T, index: number) => R
): R[] => {
  if (!isArray(array)) {
    return [];
  }
  return array.map(mapper);
};

/**
 * Valida un objeto SoftSkillResult
 */
export const isValidSoftSkill = (skill: unknown): skill is {
  skill: string;
  score: number;
  level: string;
  confidence?: number;
} => {
  if (!skill || typeof skill !== 'object') return false;
  const s = skill as { skill?: unknown; score?: unknown; level?: unknown; confidence?: unknown };
  return (
    typeof s.skill === 'string' &&
    typeof s.score === 'number' &&
    typeof s.level === 'string' &&
    ['alto', 'medio', 'bajo'].includes(s.level)
  );
};

/**
 * Valida un array de SoftSkillResult
 */
export const validateSoftSkillsArray = (skills: unknown[]): boolean => {
  if (!isValidArray(skills)) {
    return false;
  }
  
  return skills.every(isValidSoftSkill);
};

/**
 * Filtra y valida un array de SoftSkillResult
 */
export const filterValidSoftSkills = (skills: unknown[]): Array<{
  skill: string;
  score: number;
  level: 'alto' | 'medio' | 'bajo';
  confidence: number;
}> => {
  if (!isArray(skills)) {
    return [];
  }
  
  return skills.filter(isValidSoftSkill).map(skill => ({
    ...skill,
    level: skill.level as 'alto' | 'medio' | 'bajo',
    confidence: skill.confidence || 0.8 // Valor por defecto si no está presente
  }));
};

/**
 * Valida un objeto de recomendaciones
 */
export const validateRecommendations = (recommendations: unknown): {
  roles: string[];
  resources: string[];
  cvImprovements: string[];
  nextSteps: string[];
} => {
  if (!recommendations || typeof recommendations !== 'object') {
    return {
      roles: [],
      resources: [],
      cvImprovements: [],
      nextSteps: [],
    };
  }

  const rec = recommendations as Partial<{ roles: unknown[]; resources: unknown[]; cvImprovements: unknown[]; nextSteps: unknown[] }>;
  
  return {
    roles: isArray(rec.roles as string[]) ? (rec.roles as unknown[]).filter((r: unknown) => typeof r === 'string') as string[] : [],
    resources: isArray(rec.resources as string[]) ? (rec.resources as unknown[]).filter((r: unknown) => typeof r === 'string') as string[] : [],
    cvImprovements: isArray(rec.cvImprovements as string[]) ? (rec.cvImprovements as unknown[]).filter((r: unknown) => typeof r === 'string') as string[] : [],
    nextSteps: isArray(rec.nextSteps as string[]) ? (rec.nextSteps as unknown[]).filter((r: unknown) => typeof r === 'string') as string[] : [],
  };
}; 