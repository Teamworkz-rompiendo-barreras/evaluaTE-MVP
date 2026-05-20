import type { JobPreference } from '@/types/preferences';

/**
 * Normaliza las preferencias laborales garantizando un objeto con valores por defecto.
 */
export function resolveJobPreferences(personal: {
  jobPreferences?: string | Partial<JobPreference>;
  workMode?: JobPreference['workMode'];
  availability?: JobPreference['availability'];
  willingToRelocate?: boolean;
  hasDisabilityCert?: boolean;
}): JobPreference {
  const defaults: JobPreference = {
    areas: [],
    needs: [],
    workMode: personal.workMode ?? 'remoto',
    availability: personal.availability ?? 'completa',
    willingToRelocate: personal.willingToRelocate ?? false,
    hasDisabilityCert: personal.hasDisabilityCert ?? false,
  };
  const raw = personal.jobPreferences;
  if (!raw) return defaults;
  return typeof raw === 'string'
    ? { ...defaults, areas: raw ? [raw] : [] }
    : { ...defaults, ...raw };
}
