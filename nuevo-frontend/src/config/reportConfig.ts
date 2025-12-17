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
  useful_tools: UsefulTools;
  employability_score: number;
  completed_games: string[];
  final_message: string;
  job_preferences: NormalizedJobPreferences;
}

export interface NormalizedJobPreferences {
  areas: string[];
  preferred_platforms: string[];
  needs: string[];
  location: string;
  seniority: string;
  work_mode: string;
  disability_certificate: string;
  availability: string;
  willing_to_relocate: boolean;
}

const detailPriority = {
  experience: ['title', 'role', 'position', 'company', 'organization', 'employer', 'location', 'start_date', 'end_date', 'duration', 'description'] as const,
  education: ['degree', 'title', 'program', 'area', 'institution', 'school', 'location', 'start_date', 'end_date', 'graduation_year', 'description'] as const,
  languages: ['name', 'language', 'level', 'certification'] as const,
  tools: ['name', 'tool', 'technology', 'level', 'category'] as const,
};

const toUniqueStringArray = (value: unknown): string[] => {
  const result: string[] = [];
  const seen = new Set<string>();
  const push = (entry: unknown): void => {
    if (entry === null || entry === undefined) return;
    if (Array.isArray(entry)) {
      entry.forEach(push);
      return;
    }
    if (entry instanceof Set) {
      Array.from(entry).forEach(push);
      return;
    }
    if (typeof entry === 'object') {
      const obj = entry as Record<string, unknown>;
      if (typeof obj['name'] === 'string') {
        push(obj['name']);
        return;
      }
    }
    const str =
      typeof entry === 'string'
        ? entry.trim()
        : typeof entry === 'number' || typeof entry === 'boolean'
          ? String(entry).trim()
          : '';
    if (!str) return;
    const key = str.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    result.push(str);
  };
  push(value);
  return result;
};

const firstString = (value: unknown): string => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string') return value.trim();
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (value instanceof Date) return value.toISOString();
  if (Array.isArray(value)) {
    for (const entry of value) {
      const str = firstString(entry);
      if (str) return str;
    }
    return '';
  }
  if (typeof value === 'object') {
    for (const entry of Object.values(value as Record<string, unknown>)) {
      const str = firstString(entry);
      if (str) return str;
    }
  }
  return '';
};

const toBoolean = (value: unknown): boolean => {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value !== 0;
  if (typeof value === 'string') {
    const val = value.trim().toLowerCase();
    return ['1', 'true', 'si', 'sí', 'yes', 'y'].includes(val);
  }
  return false;
};

const formatDisabilityCertificate = (value: unknown): string => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'boolean') {
    return value ? 'Sí' : 'No';
  }
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (!trimmed) return '';
    if (/^(si|sí|yes|true)$/i.test(trimmed)) return 'Sí';
    if (/^(no|false)$/i.test(trimmed)) return 'No';
    return trimmed;
  }
  if (Array.isArray(value)) {
    for (const entry of value) {
      const str = formatDisabilityCertificate(entry);
      if (str) return str;
    }
    return '';
  }
  return String(value);
};

const normalizeJobPreferences = (...sources: unknown[]): NormalizedJobPreferences => {
  const merged: Record<string, unknown> = {};
  for (const source of sources) {
    if (source && typeof source === 'object' && !Array.isArray(source)) {
      Object.assign(merged, source as Record<string, unknown>);
    }
  }

  const areasSource =
    merged['areas'] ??
    merged['desired_roles'] ??
    merged['desiredRoles'] ??
    merged['roles'] ??
    merged['targets'] ??
    [];

  const preferredPlatformsSource =
    merged['preferred_platforms'] ??
    merged['preferredPlatforms'] ??
    merged['platforms'] ??
    merged['sites'] ??
    merged['channels'] ??
    [];

  const locationValue =
    merged['location'] ??
    merged['ubicacion'] ??
    merged['city'] ??
    merged['region'] ??
    merged['preferred_location'];

  const seniorityValue =
    merged['seniority'] ??
    merged['experience_level'] ??
    merged['experienceLevel'] ??
    merged['level'] ??
    merged['seniority_level'];

  const workModeValue =
    merged['work_mode'] ??
    merged['workMode'] ??
    merged['mode'] ??
    merged['working_mode'] ??
    merged['modalidad'];

  const disabilityValue =
    merged['disability_certificate'] ??
    merged['disabilityCertificate'] ??
    merged['has_disability_certificate'] ??
    merged['hasDisabilityCert'] ??
    merged['disability_cert'];

  return {
    areas: toUniqueStringArray(areasSource),
    preferred_platforms: toUniqueStringArray(preferredPlatformsSource),
    needs: toUniqueStringArray(
      merged['needs'] ??
        merged['apoyos'] ??
        merged['supports'] ??
        []
    ),
    location: firstString(locationValue),
    seniority: firstString(seniorityValue),
    work_mode: firstString(workModeValue),
    disability_certificate: formatDisabilityCertificate(disabilityValue),
    availability: firstString(
      merged['availability'] ??
        merged['schedule'] ??
        merged['disponibilidad']
    ),
    willing_to_relocate: toBoolean(
      merged['willingToRelocate'] ??
        merged['willing_to_relocate'] ??
        merged['relocate']
    ),
  };
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

export function convertBackendResponseToNewFormat(raw: unknown): NewReportSchema {
  const ensureText = (value: unknown, fallback: string): string => {
    const text = typeof value === 'string' ? value.trim() : '';
    return text.length > 0 ? text : fallback;
  };

  if (raw && typeof raw === 'object') {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const data: any = raw;
    const score = typeof data.employability_score === 'number'
      ? data.employability_score
      : typeof data.employabilityScore === 'number'
        ? data.employabilityScore
        : undefined;
    // Already in new format
    if (data.personal_data) {
      const normalizedJobPrefs = normalizeJobPreferences(
        data.job_preferences,
        data.jobPreferences,
        data.job_preferences_data,
        data.jobPreferencesData,
      );
      const rawDetails = data.cv_details || {};
      const normalizedDetails = buildCvDetails({
        experience: [rawDetails.experience, rawDetails.experience_highlights, data.cv_analysis?.experience, data.cv_analysis?.experience_detailed],
        education: [rawDetails.education, data.cv_analysis?.education, data.cv_analysis?.education_detailed],
        languages: [rawDetails.languages, data.cv_analysis?.languages],
        tools: [rawDetails.tools, rawDetails.software, data.cv_analysis?.tools, data.cv_analysis?.software],
      });
      const profileSummary = ensureText(data.profile_summary, ensureText(data.summary, 'Perfil profesional en desarrollo.'));
      const cvSummary = ensureText(data.cv_summary, profileSummary);
      const summary = ensureText(data.summary, profileSummary);
      return {
        ...data,
        summary,
        profile_summary: profileSummary,
        cv_summary: cvSummary,
        cv_details: normalizedDetails,
        personal_data: {
          name: ensureText(data.personal_data?.name, 'Usuario'),
          location: ensureText(data.personal_data?.location, 'No consta'),
          email: ensureText(data.personal_data?.email, 'No consta'),
          phone: ensureText(data.personal_data?.phone, 'No especificado'),
          disability_certificate: ensureText(
            (data.personal_data as { disability_certificate?: unknown })?.disability_certificate,
            ''
          ),
        },
        strengths: Array.isArray(data.strengths) && data.strengths.length > 0 ? data.strengths : [],
        soft_skills: Array.isArray(data.soft_skills) ? data.soft_skills : [],
        improvement_areas: Array.isArray(data.improvement_areas) ? data.improvement_areas : [],
        job_preferences: normalizedJobPrefs,
        employability_score: score ?? 0,
      } as NewReportSchema;
    }
    // Old format conversion
    if (data.report) {
      const report = data.report || {};
      const recs = (data.recommendations && typeof data.recommendations === 'object') ? data.recommendations : {};
      const jobPreferences = normalizeJobPreferences(
        report.job_preferences,
        report.jobPreferences,
        report.job_preferences_data,
        report.jobPreferencesData,
        data.job_preferences,
        data.jobPreferences,
        data.job_preferences_data,
        data.jobPreferencesData,
        recs.job_preferences,
        recs.jobPreferences,
      );

      // Personal data: preferir report.personal_data si existe
      const pdSrc = report.personal_data || {};
      const personal_data = {
        name: pdSrc.name ?? report.fullName ?? data.fullName ?? 'Desconocido',
        location: pdSrc.location ?? report.location ?? jobPreferences.location ?? '',
        email: pdSrc.email ?? report.email ?? '',
        phone: pdSrc.phone ?? report.phone ?? '',
        disability_certificate:
          pdSrc.disability_certificate
          ?? report.disability_certificate
          ?? jobPreferences.disability_certificate
          ?? ''
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

      // Soft skills (capturar múltiples variantes de estructura y nombres de campos)
      let soft_skills: Array<{ skill: string; score: number }> = [];
      const toName = (obj: Record<string, unknown>): string => {
        const candidates = [obj['skill'], obj['name'], obj['softskill'], obj['label'], obj['title']];
        for (const c of candidates) {
          const v = typeof c === 'string' ? c.trim() : (typeof c === 'number' ? String(c) : '');
          if (v) return v;
        }
        return '';
      };
      const toScore = (obj: Record<string, unknown>): number => {
        const candidates = [obj['score'], obj['value'], obj['percent'], obj['percentage'], obj['puntuacion'], obj['puntaje'], obj['val']];
        for (const c of candidates) {
          const n = Number(c);
          if (!Number.isNaN(n)) return Math.max(0, Math.min(100, Math.round(n <= 1 ? n * 100 : n)));
        }
        return 0;
      };
      const mapSkills = (arr: Array<Record<string, unknown>> | unknown): Array<{ skill: string; score: number }> => {
        if (!Array.isArray(arr)) return [];
        return arr.map((s) => {
          const obj = (s && typeof s === 'object') ? (s as Record<string, unknown>) : {};
          return { skill: toName(obj), score: toScore(obj) };
        }).filter((s) => s.skill !== '');
      };

      if (Array.isArray(report.soft_skills)) {
        soft_skills = mapSkills(report.soft_skills as Array<Record<string, unknown>>);
      } else if (Array.isArray((data as any).softSkills)) {
        soft_skills = mapSkills((data as any).softSkills as Array<Record<string, unknown>>);
      } else if (Array.isArray((data as any).soft_skills)) {
        soft_skills = mapSkills((data as any).soft_skills as Array<Record<string, unknown>>);
      } else if (Array.isArray((report as any)?.ui?.soft_skills)) {
        soft_skills = mapSkills((report as any).ui.soft_skills as Array<Record<string, unknown>>);
      } else if (Array.isArray((recs as any)?.soft_skills)) {
        soft_skills = mapSkills((recs as any).soft_skills as Array<Record<string, unknown>>);
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
      const reportRecommendedPlatforms = Array.isArray(report?.job_search_advice?.recommended_platforms)
        ? (report.job_search_advice.recommended_platforms as unknown[])
            .map((platform) => (platform === null || platform === undefined ? '' : String(platform).trim()))
            .filter((platform): platform is string => Boolean(platform))
        : undefined;
      const job_search_advice = {
        cv_optimization: Array.isArray(report?.job_search_advice?.cv_optimization)
          ? report.job_search_advice.cv_optimization
          : (Array.isArray(report?.job_search_advice?.tips) ? report.job_search_advice.tips : []),
        letters_portfolio: String(report?.job_search_advice?.letters_portfolio ?? ''),
        recommended_platforms: reportRecommendedPlatforms && reportRecommendedPlatforms.length > 0
          ? reportRecommendedPlatforms
          : jobPreferences.preferred_platforms,
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
            seniority: String(r?.seniority ?? jobPreferences.seniority ?? ''),
            remote_viable: typeof r?.remote_viable === 'boolean'
              ? Boolean(r?.remote_viable)
              : (jobPreferences.work_mode || '').toLowerCase() === 'remoto',
          }))
        : [];

      // Otros campos
      const jobPreferenceEnvironment = [
        jobPreferences.work_mode ? `Modalidad preferida: ${jobPreferences.work_mode}` : '',
        jobPreferences.areas.length ? `Áreas de interés: ${jobPreferences.areas.join(', ')}` : '',
        jobPreferences.location ? `Ubicación deseada: ${jobPreferences.location}` : '',
      ].filter(Boolean).join(' — ');
      const ideal_work_environment = String(
        recs?.entornos_ideales
          || (Array.isArray(report?.environments) ? report.environments.join(', ') : '')
          || jobPreferenceEnvironment
          || ''
      );
      const completed_games = Array.isArray(report?.completed_games) ? report.completed_games.map(String) : [];
      const final_message = String(recs?.frase_final || report?.frase_final || '');

      // Resúmenes
      const profile_summary = ensureText(
        recs?.resumen_perfil || report?.resumen_ejecutivo || data?.summary,
        'Perfil profesional con potencial de desarrollo.'
      );
      const summary = ensureText(
        report?.resumen_ejecutivo || data?.summary || profile_summary,
        profile_summary
      );
      const cv_summary = ensureText(recs?.resumen_cv, profile_summary);

      return {
        summary,
        personal_data,
        job_preferences: jobPreferences,
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
  const prefs = data.job_preferences || {
    areas: [],
    needs: [],
    preferred_platforms: [],
    location: '',
    seniority: '',
    work_mode: '',
    disability_certificate: '',
    availability: '',
    willing_to_relocate: false,
  };

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
    '## 2. Preferencias laborales',
    ...(prefs.areas?.length ? [`Áreas preferidas: ${prefs.areas.join(', ')}`] : []),
    ...(prefs.needs?.length ? [`Apoyos o necesidades: ${prefs.needs.join(', ')}`] : []),
    ...(prefs.work_mode ? [`Modalidad deseada: ${prefs.work_mode}`] : []),
    ...(prefs.availability ? [`Disponibilidad: ${prefs.availability}`] : []),
    ...(prefs.location ? [`Ubicación deseada: ${prefs.location}`] : []),
    ...(prefs.preferred_platforms?.length ? [`Plataformas favoritas: ${prefs.preferred_platforms.join(', ')}`] : []),
    ...(prefs.disability_certificate ? [`Certificado de discapacidad: ${prefs.disability_certificate}`] : []),
    ...(typeof prefs.willing_to_relocate === 'boolean'
      ? [`Movilidad geográfica: ${prefs.willing_to_relocate ? 'Sí' : 'No'}`]
      : []),
    '',
    '## 3. Resumen del perfil',
    data.profile_summary,
    '',
    '## 4. Resumen del CV',
    data.cv_summary,
    ...detailSectionLines,
    '## 5. Fortalezas',
    ...data.strengths.map((s) => `- ${s}`),
    '',
    // Título como H1 para que el split en ResultadosPage lo detecte (# ... Áreas de mejora ...)
    '# 6. Áreas de mejora y consejos',
    ...data.improvement_areas.map(
      (a) => `- ${a.area} - ${a.reason}${a.suggested_action ? ` (Acción: ${a.suggested_action})` : ''}`
    ),
    '',
    '## 7. Análisis del CV con puntuación 1–5',
    `Estructura: ${stars(data.cv_analysis.structure_score)}`,
    `Coherencia: ${stars(data.cv_analysis.coherence_score)}`,
    `Información clave: ${stars(data.cv_analysis.key_info_score)}`,
    `Claridad: ${stars(data.cv_analysis.clarity_score)}`,
    `Estilo: ${stars(data.cv_analysis.style_score)}`,
    '',
    '## 8. Entornos de trabajo ideales',
    data.ideal_work_environment,
    '',
    '## 9. Roles profesionales sugeridos',
    ...data.suggested_roles.map((r) => `- ${r.role} - ${r.reason}`),
    '',
    '## 10. Plan de acción',
    'Corto plazo:',
    ...data.action_plan.short_term.map((s) => `- ${s}`),
    'Mediano plazo:',
    ...data.action_plan.medium_term.map((s) => `- ${s}`),
    'Largo plazo:',
    ...data.action_plan.long_term.map((s) => `- ${s}`),
    '',
    '## 11. Consejos de búsqueda de empleo',
    'Optimización del CV:',
    ...data.job_search_advice.cv_optimization.map((tip) => `- ${tip}`),
    `Cartas y portafolio: ${data.job_search_advice.letters_portfolio}`,
    `Plataformas recomendadas: ${data.job_search_advice.recommended_platforms.join(', ')}`,
    `Networking: ${data.job_search_advice.networking}`,
    `Entrevistas: ${data.job_search_advice.interview_tips}`,
    '',
    '## 12. Herramientas útiles y tecnología',
    ...[
      ['Productividad', data.useful_tools.productivity],
      ['Búsqueda de empleo', data.useful_tools.job_search],
      ['Aprendizaje', data.useful_tools.learning],
      ['Accesibilidad', data.useful_tools.accessibility],
    ].map(([label, items]) => `${label}: ${(items as string[]).join(', ')}`),
    '',
    '## 13. Juegos completados',
    ...prettyGames.map((g) => `- ${g}`),
  ];

  return lines.join('\n');
}
