// src/pages/processRadarData.ts

export interface RadarInputItem {
  skill?: string;
  softskill?: string;
  score: number;
}

export interface RadarOutputItem {
  softskill: string;
  score: number;
  [key: string]: unknown;
}

export const ALL_RADAR_SKILLS = [
  'Toma de decisiones',
  'Pensamiento analítico',
  'Creatividad',
  'Influencia social',
  'Curiosidad y aprendizaje',
  'Resiliencia y flexibilidad',
  'Autoconciencia',
  'Empatía',
  'Pensamiento Crítico',
  'Liderazgo',
] as const;

const normalizeRadarLabel = (s: unknown): string =>
  String(s || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();

const RADAR_SYNONYMS: Record<string, string> = {
  'capacidad de aprendizaje': 'Curiosidad y aprendizaje',
  'aprendizaje': 'Curiosidad y aprendizaje',
  'adaptabilidad': 'Resiliencia y flexibilidad',
  'adaptabilidad al cambio': 'Resiliencia y flexibilidad',
  'trabajo en equipo': 'Influencia social',
  'comunicacion': 'Influencia social',
  'resolucion de problemas': 'Pensamiento analítico',
  'pensamiento analitico': 'Pensamiento analítico',
  'pensamiento critico': 'Pensamiento Crítico',
  'liderazgo de equipos': 'Liderazgo',
  'autoconocimiento': 'Autoconciencia',
};

export function processRadarData(data: Array<RadarInputItem>): RadarOutputItem[] {
  if (!Array.isArray(data)) {
    return ALL_RADAR_SKILLS.map((label) => ({ softskill: label, score: 0 }));
  }

  const canonicalEntries = new Map<string, { label: string; score: number }>();

  const ensureUnion = (label: string, target: string[], seen: Set<string>) => {
    const key = normalizeRadarLabel(label);
    if (!seen.has(key)) {
      seen.add(key);
      target.push(label);
    }
  };

  const unionLabels: string[] = [];
  const unionSeen = new Set<string>();
  for (const label of ALL_RADAR_SKILLS) {
    ensureUnion(label, unionLabels, unionSeen);
  }

  for (const raw of data) {
    const labelRaw = String(raw?.skill || raw?.softskill || '').trim();
    if (!labelRaw) continue;

    const rawKey = normalizeRadarLabel(labelRaw);
    const canonicalLabel =
      RADAR_SYNONYMS[rawKey] || ALL_RADAR_SKILLS.find((s) => normalizeRadarLabel(s) === rawKey) || labelRaw;
    const canonicalKey = normalizeRadarLabel(canonicalLabel);
    const score = Math.max(0, Math.min(100, Math.round(Number((raw as any)?.score) || 0)));

    const prev = canonicalEntries.get(canonicalKey);
    const nextScore = Math.max(prev?.score ?? 0, score);
    const labelToUse = prev?.label ?? canonicalLabel;
    canonicalEntries.set(canonicalKey, { label: labelToUse, score: nextScore });

    ensureUnion(canonicalLabel, unionLabels, unionSeen);
  }

  return unionLabels.map((label) => {
    const key = normalizeRadarLabel(label);
    const entry = canonicalEntries.get(key);
    return {
      softskill: label,
      score: entry?.score ?? 0,
    };
  });
}

export default processRadarData;
