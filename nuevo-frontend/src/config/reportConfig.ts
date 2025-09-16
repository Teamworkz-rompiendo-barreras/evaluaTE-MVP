import type { CvAnalysis } from '../types/report';

export interface PersonalData {
  name: string;
  location: string;
  email: string;
  phone: string;
  disability_certificate: string;
}

export interface ImprovementArea {
  area: string;
  reason: string;
  suggested_action: string;
}

export interface SuggestedRole {
  role: string;
  reason: string;
  seniority: string;
  remote_viable: boolean;
}

export interface ActionPlan {
  short_term: string[];
  medium_term: string[];
  long_term: string[];
}

export interface JobSearchAdvice {
  cv_optimization: string[];
  letters_portfolio: string;
  recommended_platforms: string[];
  networking: string;
  interview_tips: string;
}

export interface UsefulTools {
  productivity: string[];
  job_search: string[];
  learning: string[];
  accessibility: string[];
}

export interface JobPreferences {
  location: string;
  work_mode: string;
  areas: string[];
  preferred_platforms: string[];
  seniority: string;
  has_disability_cert: boolean;
}

export interface CvDetails {
  experience: string[];
  education: string[];
  languages: string[];
  tools: string[];
}

export interface NewReportSchema {
  summary: string;
  personal_data: PersonalData;
  profile_summary: string;
  cv_summary: string;
  cv_details: CvDetails;
  strengths: string[];
  soft_skills: Array<{ skill: string; score: number }>;
  improvement_areas: ImprovementArea[];
  cv_analysis: CvAnalysis;
  ideal_work_environment: string;
  suggested_roles: SuggestedRole[];
  action_plan: ActionPlan;
  job_search_advice: JobSearchAdvice;
  job_preferences: JobPreferences;
  useful_tools: UsefulTools;
  employability_score: number;
  completed_games: string[];
  final_message: string;
}

const detailPriority = {
  experience: ['title', 'role', 'position', 'company', 'organization', 'employer', 'location', 'start_date', 'end_date', 'duration', 'description'] as const,
  education: ['degree', 'title', 'program', 'area', 'institution', 'school', 'location', 'start_date', 'end_date', 'graduation_year', 'description'] as const,
  languages: ['name', 'language', 'level', 'certification'] as const,
  tools: ['name', 'tool', 'technology', 'level', 'category'] as const,
};

const stringifyDetailEntry = (entry: unknown, priorityKeys: readonly string[]): string | null => {
  if (entry === null || entry === undefined) return null;
  if (typeof entry === 'string') {
    const trimmed = entry.trim();
    return trimmed ? trimmed : null;
  }
  if (typeof entry === 'number' || typeof entry === 'boolean') {
    const str = String(entry).trim();
    return str ? str : null;
  }
  if (entry instanceof Date) {
    return entry.toISOString();
  }
  if (typeof entry === 'object') {
    const obj = entry as Record<string, unknown>;
    const parts: string[] = [];
    const used = new Set<string>();
    for (const key of priorityKeys) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        const value = obj[key];
        if (value === null || value === undefined) continue;
        if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
          const str = String(value).trim();
          if (str) {
            parts.push(str);
            used.add(key);
          }
        }
      }
    }
    if (!parts.length) {
      for (const [key, value] of Object.entries(obj)) {
        if (used.has(key) || value === null || value === undefined) continue;
        if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
          const str = String(value).trim();
          if (str) parts.push(str);
        }
      }
    }
    const joined = parts.join(' — ');
    return joined || null;
  }
  const str = String(entry).trim();
  return str ? str : null;
};

const normalizeDetailList = (input: unknown, priorityKeys: readonly string[]): string[] => {
  const result: string[] = [];
  const seen = new Set<string>();
  const pushEntry = (value: unknown): void => {
    if (value === null || value === undefined) return;
    if (value instanceof Date) {
      pushEntry(value.toISOString());
      return;
    }
    if (Array.isArray(value)) {
      value.forEach(pushEntry);
      return;
    }
    if (typeof value === 'object' && value !== null) {
      const obj = value as Record<string, unknown>;
      const values = Object.values(obj);
      if (values.some((child) => Array.isArray(child))) {
        values.forEach(pushEntry);
        return;
      }
    }
    const formatted = stringifyDetailEntry(value, priorityKeys);
    if (formatted) {
      const key = formatted.toLowerCase();
      if (!seen.has(key)) {
        seen.add(key);
        result.push(formatted);
      }
    }
  };
  pushEntry(input);
  return result;
};

const buildCvDetails = (sources: Partial<Record<keyof CvDetails, unknown>>): CvDetails => ({
  experience: normalizeDetailList(sources.experience, detailPriority.experience),
  education: normalizeDetailList(sources.education, detailPriority.education),
  languages: normalizeDetailList(sources.languages, detailPriority.languages),
  tools: normalizeDetailList(sources.tools, detailPriority.tools),
});

const coerceString = (value: unknown): string => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string') return value.trim();
  return String(value).trim();
};

const coerceBoolean = (value: unknown): boolean => {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value !== 0;
  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase();
    if (['true', '1', 'yes', 'si', 'sí'].includes(normalized)) return true;
    if (['false', '0', 'no'].includes(normalized)) return false;
  }
  return false;
};

const normalizeJobPreferenceList = (input: unknown): string[] =>
  normalizeDetailList(input, ['role', 'title', 'name', 'area', 'label', 'value']);

const mergeJobPreferenceSources = (...sources: Array<unknown>): Record<string, unknown> => {
  const merged: Record<string, unknown> = {};
  for (const source of sources) {
    if (source && typeof source === 'object' && !Array.isArray(source)) {
      Object.assign(merged, source as Record<string, unknown>);
    }
  }
  return merged;
};

const normalizeJobPreferences = (...sources: Array<unknown>): JobPreferences => {
  const merged = mergeJobPreferenceSources(...sources);
  const areasSource =
    merged.areas ?? merged.desired_roles ?? merged.desiredRoles ?? merged.roles ?? merged.targets ?? [];
  const preferredPlatformsSource =
    merged.preferred_platforms ??
    merged.preferredPlatforms ??
    merged.platforms ??
    merged.recommended_platforms ??
    merged.recommendedPlatforms ??
    [];
  let location = coerceString(merged.location ?? merged.city ?? merged.region ?? '');
  if (location.toLowerCase() === 'no especificado') location = '';
  const seniority = coerceString(merged.seniority ?? merged.level ?? merged.targetLevel ?? '') || 'Senior';
  const workMode = coerceString(merged.work_mode ?? merged.workMode ?? merged.mode ?? merged.modality ?? '');
  const hasCertSource =
    merged.has_disability_cert ??
    merged.hasDisabilityCert ??
    merged.disability_certificate ??
    merged.disabilityCertificate ??
    merged.disability ??
    merged.certificate;

  return {
    location,
    work_mode: workMode,
    areas: normalizeJobPreferenceList(areasSource),
    preferred_platforms: normalizeJobPreferenceList(preferredPlatformsSource),
    seniority,
    has_disability_cert: hasCertSource !== undefined ? coerceBoolean(hasCertSource) : false,
  };
};

export function convertBackendResponseToNewFormat(raw: unknown): NewReportSchema {
  if (raw && typeof raw === 'object') {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const data: any = raw;
    const score = typeof data.employability_score === 'number'
      ? data.employability_score
      : typeof data.employabilityScore === 'number'
        ? data.employabilityScore
        : undefined;
    // Already in new format
    if (data.summary && data.personal_data) {
      const rawDetails = data.cv_details || {};
      const normalizedDetails = buildCvDetails({
        experience: [rawDetails.experience, rawDetails.experience_highlights, data.cv_analysis?.experience, data.cv_analysis?.experience_detailed],
        education: [rawDetails.education, data.cv_analysis?.education, data.cv_analysis?.education_detailed],
        languages: [rawDetails.languages, data.cv_analysis?.languages],
        tools: [rawDetails.tools, rawDetails.software, data.cv_analysis?.tools, data.cv_analysis?.software],
      });
      const job_preferences = normalizeJobPreferences(
        {
          location: data.personal_data?.location ?? '',
          hasDisabilityCert: data.personal_data?.disability_certificate,
          preferred_platforms: data.job_search_advice?.recommended_platforms,
        },
        data.job_preferences,
        data.jobPreferences,
        data.job_preferences_data,
      );
      return {
        ...data,
        cv_details: normalizedDetails,
        job_preferences,
        employability_score: score ?? 0,
      } as NewReportSchema;
    }
    // Old format conversion
    if (data.report) {
      const report = data.report || {};
      const recs = (data.recommendations && typeof data.recommendations === 'object') ? data.recommendations : {};

      // Personal data: preferir report.personal_data si existe
      const pdSrc = report.personal_data || {};
      const personal_data = {
        name: pdSrc.name ?? report.fullName ?? data.fullName ?? 'Desconocido',
        location: pdSrc.location ?? report.location ?? '',
        email: pdSrc.email ?? report.email ?? '',
        phone: pdSrc.phone ?? report.phone ?? '',
        disability_certificate: pdSrc.disability_certificate ?? report.disability_certificate ?? ''
      };

      // CV analysis: usar report.cv_analysis.analysis_json si existe; fallback a estrellas
      const cvA = report.cv_analysis || {};
      const analysisJson = (cvA.analysis_json && typeof cvA.analysis_json === 'object') ? cvA.analysis_json : {};
      const stars = (cvA.stars && typeof cvA.stars === 'object') ? cvA.stars : {} as Record<string, unknown>;
      const parseStars = (val: unknown): number => {
        if (typeof val === 'number') return val;
        if (typeof val === 'string') {
          const count = (val.match(/★/g) || []).length;
          if (count > 0) return count;
        }
        return 0;
      };

      const cv_analysis = {
        structure_score: typeof analysisJson.structure_score === 'number' ? analysisJson.structure_score : parseStars(stars['formato']),
        coherence_score: typeof analysisJson.coherence_score === 'number' ? analysisJson.coherence_score : parseStars(stars['coherencia']),
        key_info_score: typeof analysisJson.key_info_score === 'number' ? analysisJson.key_info_score : parseStars(stars['informacion_clave']),
        clarity_score: typeof analysisJson.clarity_score === 'number' ? analysisJson.clarity_score : parseStars(stars['claridad']),
        style_score: typeof analysisJson.spelling_style_score === 'number' ? analysisJson.spelling_style_score : parseStars(stars['ortografia']),
        evidence: {
          structure: String(analysisJson?.evidence?.structure ?? ''),
          coherence: String(analysisJson?.evidence?.coherence ?? ''),
          key_info: String(analysisJson?.evidence?.key_info ?? ''),
          clarity: String(analysisJson?.evidence?.clarity ?? ''),
          style: String(analysisJson?.evidence?.style ?? ''),
        },
        corrections: Array.isArray(analysisJson?.corrections) ? analysisJson.corrections : [],
        reordering_suggestions: Array.isArray(analysisJson?.reordering_suggestions) ? analysisJson.reordering_suggestions : [],
      } as CvAnalysis;

      // Soft skills
      let soft_skills: Array<{ skill: string; score: number }> = [];
      if (Array.isArray(report.soft_skills)) {
        soft_skills = (report.soft_skills as Array<Record<string, unknown>>).map((s) => ({
          skill: String(s['skill'] ?? s['name'] ?? ''),
          score: Number(s['score'] ?? 0),
        }));
      } else if (Array.isArray(data.softSkills)) {
        soft_skills = (data.softSkills as Array<Record<string, unknown>>).map((s) => ({
          skill: String(s['skill'] ?? s['name'] ?? ''),
          score: Number(s['score'] ?? 0),
        }));
      }

      // Fortalezas
      let strengths: string[] = [];
      if (Array.isArray(recs.fortalezas_clave)) {
        strengths = recs.fortalezas_clave.map((s: unknown) => String(s));
      } else if (soft_skills.length > 0) {
        strengths = soft_skills.filter((s) => (Number(s.score) || 0) >= 70).map((s) => s.skill);
      }

      // Áreas de mejora
      let improvement_areas = [] as ImprovementArea[];
      if (Array.isArray(recs.areas_mejora)) {
        improvement_areas = recs.areas_mejora.map((a: any) => ({
          area: String(a?.area ?? a ?? ''),
          reason: String(a?.reason ?? ''),
          suggested_action: String(a?.suggested_action ?? ''),
        }));
      } else if (Array.isArray(report.improvement_areas)) {
        improvement_areas = report.improvement_areas.map((a: any) => ({
          area: String(a?.area ?? a ?? ''),
          reason: String(a?.reason ?? ''),
          suggested_action: String(a?.suggested_action ?? ''),
        }));
      }

      // Plan de acción
      const action_plan = {
        short_term: Array.isArray(report?.action_plan?.short_term) ? report.action_plan.short_term : [],
        medium_term: Array.isArray(report?.action_plan?.medium_term) ? report.action_plan.medium_term : [],
        long_term: Array.isArray(report?.action_plan?.long_term) ? report.action_plan.long_term : [],
      };

      // Consejos de búsqueda
      const job_search_advice = {
        cv_optimization: Array.isArray(report?.job_search_advice?.cv_optimization)
          ? report.job_search_advice.cv_optimization
          : (Array.isArray(report?.job_search_advice?.tips) ? report.job_search_advice.tips : []),
        letters_portfolio: String(report?.job_search_advice?.letters_portfolio ?? ''),
        recommended_platforms: Array.isArray(report?.job_search_advice?.recommended_platforms)
          ? report.job_search_advice.recommended_platforms
          : [],
        networking: String(report?.job_search_advice?.networking ?? ''),
        interview_tips: String(report?.job_search_advice?.interview_tips ?? ''),
      };

      // Herramientas
      const useful_tools = {
        productivity: Array.isArray(report?.tools?.productivity) ? report.tools.productivity.filter(Boolean) : [],
        job_search: Array.isArray(report?.tools?.job_search) ? report.tools.job_search.filter(Boolean) : [],
        learning: Array.isArray(report?.tools?.learning) ? report.tools.learning.filter(Boolean) : [],
        accessibility: Array.isArray(report?.tools?.accessibility) ? report.tools.accessibility.filter(Boolean) : [],
      };

      const cvDetailsSource = report.cv_details || {};
      const cv_details = buildCvDetails({
        experience: [
          cvDetailsSource.experience,
          report.experience,
          report.experiencia,
          cvA?.experience,
          cvA?.experience_detailed,
          analysisJson?.experience,
          analysisJson?.experience_detailed,
          data?.cv_analysis?.experience,
          data?.cv_analysis?.experience_detailed,
        ],
        education: [
          cvDetailsSource.education,
          report.education,
          report.educacion,
          report.education_history,
          cvA?.education,
          cvA?.education_detailed,
          analysisJson?.education,
          analysisJson?.education_detailed,
          data?.cv_analysis?.education,
          data?.cv_analysis?.education_detailed,
        ],
        languages: [
          cvDetailsSource.languages,
          report.languages,
          report.idiomas,
          cvA?.languages,
          analysisJson?.languages,
          data?.cv_analysis?.languages,
        ],
        tools: [
          cvDetailsSource.tools,
          report.tools,
          report.software,
          cvA?.tools,
          cvA?.software,
          cvA?.skills,
          analysisJson?.tools,
          analysisJson?.software,
          data?.cv_analysis?.tools,
          data?.cv_analysis?.software,
        ],
      });

      // Roles sugeridos
      const suggested_roles = Array.isArray(report?.suggested_roles)
        ? report.suggested_roles.map((r: any) => ({
            role: String(r?.role ?? r?.name ?? ''),
            reason: String(r?.reason ?? ''),
            seniority: String(r?.seniority ?? ''),
            remote_viable: Boolean(r?.remote_viable),
          }))
        : [];

      // Otros campos
      const ideal_work_environment = String(
        recs?.entornos_ideales
          || (Array.isArray(report?.environments) ? report.environments.join(', ') : '')
          || ''
      );
      const completed_games = Array.isArray(report?.completed_games) ? report.completed_games.map(String) : [];
      const final_message = String(recs?.frase_final || report?.frase_final || '');

      // Resúmenes
      const profile_summary = String(recs?.resumen_perfil || report?.resumen_ejecutivo || data?.summary || '');
      const summary = String(report?.resumen_ejecutivo || data?.summary || profile_summary || '');
      const cv_summary = String(recs?.resumen_cv || '');

      const job_preferences = normalizeJobPreferences(
        {
          location: personal_data.location,
          hasDisabilityCert: personal_data.disability_certificate,
          preferred_platforms: job_search_advice.recommended_platforms,
        },
        data.job_preferences,
        data.jobPreferences,
        report?.job_preferences,
        report?.jobPreferences,
        report?.job_preferences_data,
        report?.jobPreferencesData,
        {
          work_mode: data.workMode ?? data.work_mode ?? report?.workMode ?? report?.work_mode,
          seniority: data.seniority ?? report?.seniority ?? data.level,
        },
      );

      return {
        summary,
        personal_data,
        profile_summary,
        cv_summary,
        strengths,
        soft_skills,
        improvement_areas,
        cv_analysis,
        cv_details,
        ideal_work_environment,
        suggested_roles,
        action_plan,
        job_search_advice,
        job_preferences,
        useful_tools,
        employability_score: score ?? 0,
        completed_games,
        final_message,
      };
    }
  }
  throw new Error('Formato de datos desconocido');
}

export function generateNewFormatReport(data: NewReportSchema): string {
  // Mapeo legible para slugs de minijuegos → títulos en español
  const gameNameMap: Record<string, string> = {
    'decision-making': 'Toma de decisiones',
    'analytical-thinking': 'Pensamiento analítico',
    'creativity': 'Creatividad',
    'social-influence': 'Influencia social',
    'curiosity-learning': 'Curiosidad y aprendizaje',
    'resilience-flexibility': 'Resiliencia y flexibilidad',
    'self-awareness': 'Autoconciencia',
    'empathy': 'Empatía',
    'critical-thinking': 'Pensamiento crítico',
    'leadership': 'Liderazgo',
  };

  const prettyGames = (data.completed_games || []).map((g) =>
    gameNameMap[g] ?? g.replace(/-/g, ' ')
  );
  const radarData = data.soft_skills.map(s => ({ softskill: s.skill, score: s.score }));

  const stars = (n: number): string => {
    const v = Math.max(0, Math.min(5, Math.round(n)));
    return '★'.repeat(v) + '☆'.repeat(5 - v);
  };

  const detailSectionLines: string[] = [''];
  const addDetailSection = (title: string, items?: string[]): void => {
    if (!items || items.length === 0) return;
    const normalized = items
      .map((item) => String(item ?? '').trim())
      .filter((item) => item.length > 0);
    if (normalized.length === 0) return;
    detailSectionLines.push(title);
    normalized.forEach((item) => detailSectionLines.push(`- ${item}`));
    detailSectionLines.push('');
  };

  addDetailSection('### Experiencia destacada', data.cv_details?.experience);
  addDetailSection('### Formación', data.cv_details?.education);
  addDetailSection('### Idiomas', data.cv_details?.languages);
  addDetailSection('### Herramientas y tecnología', data.cv_details?.tools);

  if (detailSectionLines.length === 1) {
    // Mantener una línea en blanco para separar secciones aunque no haya detalles.
    detailSectionLines[0] = '';
  }

  const jobPref: JobPreferences = data.job_preferences ?? {
    location: '',
    work_mode: '',
    areas: [],
    preferred_platforms: [],
    seniority: 'Senior',
    has_disability_cert: false,
  };
  const preferenceLines: string[] = ['## 7. Preferencias laborales y entorno ideal'];
  const preferenceItems = [
    jobPref.work_mode && `Modalidad preferida: ${jobPref.work_mode}`,
    jobPref.areas.length > 0 ? `Áreas de interés: ${jobPref.areas.join(', ')}` : null,
    jobPref.preferred_platforms.length > 0
      ? `Plataformas preferidas: ${jobPref.preferred_platforms.join(', ')}`
      : null,
    jobPref.seniority && `Seniority objetivo: ${jobPref.seniority}`,
    jobPref.location && `Ubicación objetivo: ${jobPref.location}`,
    `Certificado de discapacidad: ${jobPref.has_disability_cert ? 'Sí' : 'No'}`,
  ].filter((entry): entry is string => Boolean(entry));
  preferenceLines.push(...preferenceItems.map((text) => `- ${text}`));
  const environmentText = String(data.ideal_work_environment ?? '').trim();
  if (environmentText) {
    preferenceLines.push('');
    preferenceLines.push(environmentText);
  }
  preferenceLines.push('');

  const lines = [
    '```json',
    JSON.stringify({ radarData }),
    '```',
    '',
    '## 1. Datos personales básicos',
    `Nombre: ${data.personal_data.name}`,
    `Ubicación: ${data.personal_data.location}`,
    `Email: ${data.personal_data.email}`,
    `Teléfono: ${data.personal_data.phone}`,
    '',
    '## 2. Resumen del perfil',
    data.profile_summary,
    '',
    '## 3. Resumen del CV',
    data.cv_summary,
    ...detailSectionLines,
    '## 4. Fortalezas',
    ...data.strengths.map((s) => `- ${s}`),
    '',
    // Título como H1 para que el split en ResultadosPage lo detecte (# ... Áreas de mejora ...)
    '# 5. Áreas de mejora y consejos',
    ...data.improvement_areas.map(
      (a) => `- ${a.area} - ${a.reason}${a.suggested_action ? ` (Acción: ${a.suggested_action})` : ''}`
    ),
    '',
    '## 6. Análisis del CV con puntuación 1–5',
    `Estructura: ${stars(data.cv_analysis.structure_score)}`,
    `Coherencia: ${stars(data.cv_analysis.coherence_score)}`,
    `Información clave: ${stars(data.cv_analysis.key_info_score)}`,
    `Claridad: ${stars(data.cv_analysis.clarity_score)}`,
    `Estilo: ${stars(data.cv_analysis.style_score)}`,
    '',
    ...preferenceLines,
    '## 8. Roles profesionales sugeridos',
    ...data.suggested_roles.map((r) => `- ${r.role} - ${r.reason}`),
    '',
    '## 9. Plan de acción',
    'Corto plazo:',
    ...data.action_plan.short_term.map((s) => `- ${s}`),
    'Mediano plazo:',
    ...data.action_plan.medium_term.map((s) => `- ${s}`),
    'Largo plazo:',
    ...data.action_plan.long_term.map((s) => `- ${s}`),
    '',
    '## 10. Consejos de búsqueda de empleo',
    'Optimización del CV:',
    ...data.job_search_advice.cv_optimization.map((tip) => `- ${tip}`),
    `Cartas y portafolio: ${data.job_search_advice.letters_portfolio}`,
    `Plataformas recomendadas: ${data.job_search_advice.recommended_platforms.join(', ')}`,
    `Networking: ${data.job_search_advice.networking}`,
    `Entrevistas: ${data.job_search_advice.interview_tips}`,
    '',
    '## 11. Herramientas útiles y tecnología',
    ...[
      ['Productividad', data.useful_tools.productivity],
      ['Búsqueda de empleo', data.useful_tools.job_search],
      ['Aprendizaje', data.useful_tools.learning],
      ['Accesibilidad', data.useful_tools.accessibility],
    ].map(([label, items]) => `${label}: ${(items as string[]).join(', ')}`),
    '',
    '## 12. Juegos completados',
    ...prettyGames.map((g) => `- ${g}`),
    '',
    '## 13. Frase final de cierre',
    data.final_message,
  ];

  return lines.join('\n');
}
