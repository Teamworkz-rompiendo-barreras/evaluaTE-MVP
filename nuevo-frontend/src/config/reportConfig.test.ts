// src/config/reportConfig.ts

import type { CvAnalysis, CvItem } from '../types/report';
export type { CvItem };

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
  /**
   * Resumen de por qué el rol encaja con la experiencia/herramientas de la persona.
   */
  fit_by_skills?: string;
  /**
   * Lista breve de experiencias, herramientas o soft skills que sustentan la recomendación.
   */
  matched_skills?: string[];
  /**
   * Puntuación de encaje calculada por el backend.
   */
  fit_score?: number;
  /**
   * Razón de preferencia si fue seleccionado por las preferencias del candidato.
   */
  preference_reason?: string;
}

export interface ActionPlan {
  short_term: string[];
  medium_term: string[];
  long_term: string[];
}

export interface JobSearchAdvice {
  cv_optimization: string[];
  letters_portfolio: string[];
  recommended_platforms: string[];
  networking: string[];
  interview_tips: string[];
}

export interface UsefulTools {
  productivity: string[];
  job_search: string[];
  learning: string[];
  accessibility: string[];
}

export interface ReadyPhrases {
  headline: string;
  about_me: string;
  short_message: string;
}

export interface CvDetails {
  experience: CvItem[];
  education: CvItem[];
  languages: CvItem[];
  tools: CvItem[];
}

export interface NewReportSchema {
  summary?: string;
  personal_data: PersonalData;
  profile_summary: string;
  cv_analysis_summary: string;
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
  ready_phrases: ReadyPhrases;
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
  experience: ['title', 'role', 'position', 'company', 'organization', 'employer', 'location', 'start_date', 'end_date', 'duration', 'description', 'subtitle', 'period', 'detail', 'level'] as const,
  education: ['degree', 'title', 'program', 'area', 'institution', 'school', 'location', 'start_date', 'end_date', 'graduation_year', 'description', 'subtitle', 'period', 'detail', 'level'] as const,
  languages: ['name', 'language', 'level', 'certification', 'title', 'subtitle', 'period', 'detail'] as const,
  tools: ['name', 'tool', 'technology', 'level', 'category', 'title', 'subtitle', 'period', 'detail'] as const,
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

const toCvItemArray = (input: unknown, priorityKeys: readonly string[]): CvItem[] => {
  const result: CvItem[] = [];
  const seen = new Set<string>();
  const pushEntry = (value: unknown): void => {
    if (value === null || value === undefined) return;
    if (Array.isArray(value)) {
      value.forEach(pushEntry);
      return;
    }
    if (value instanceof Date) {
      result.push({ detail: value.toISOString() });
      return;
    }
    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
      const txt = String(value).trim();
      if (!txt) return;
      const key = txt.toLowerCase();
      if (seen.has(key)) return;
      seen.add(key);
      result.push({ title: txt, detail: txt });
      return;
    }
    if (typeof value === 'object' && value !== null) {
      const obj = value as Record<string, unknown>;
      const item: CvItem = {};
      for (const key of priorityKeys) {
        const v = obj[key as string];
        if (v === null || v === undefined) continue;
        const txt = String(v).trim();
        if (!txt) continue;
        switch (key) {
          case 'title':
          case 'role':
          case 'position':
          case 'name':
          case 'language':
          case 'tool':
          case 'technology':
            if (!item.title) item.title = txt;
            break;
          case 'company':
          case 'organization':
          case 'employer':
          case 'institution':
          case 'school':
          case 'subtitle':
            if (!item.subtitle) item.subtitle = txt;
            break;
          case 'period':
          case 'start_date':
          case 'end_date':
          case 'duration':
          case 'graduation_year':
            if (!item.period) item.period = txt;
            break;
          case 'degree':
          case 'program':
          case 'area':
          case 'level':
          case 'certification':
          case 'category':
            if (!item.level) item.level = txt;
            break;
          case 'description':
          case 'detail':
            if (!item.detail) item.detail = txt;
            break;
          default:
            break;
        }
      }
      if (!item.title) {
        const titleField = obj['title'] ?? obj['name'] ?? obj['language'] ?? obj['tool'];
        if (typeof titleField === 'string' && titleField.trim()) item.title = titleField.trim();
      }
      if (!item.detail) {
        const desc = obj['detail'] ?? obj['description'];
        if (typeof desc === 'string' && desc.trim()) item.detail = desc.trim();
      }
      const signature = `${item.title || ''}|${item.subtitle || ''}|${item.period || ''}|${item.level || ''}|${item.detail || ''}`.toLowerCase();
      if (signature.trim() && !seen.has(signature)) {
        seen.add(signature);
        result.push(item);
      }
      return;
    }
    const txt = String(value).trim();
    if (!txt) return;
    const key = txt.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    result.push({ title: txt, detail: txt });
  };
  pushEntry(input);
  return result;
};

const cvItemSignature = (item: CvItem): string => [
  item.title,
  item.subtitle,
  item.period,
  item.level,
  item.detail,
]
  .map((part) => (part || '').trim().toLowerCase())
  .filter(Boolean)
  .join('|');

const normalizeSuggestedRoles = (
  jobPreferences: NormalizedJobPreferences,
  ...sources: unknown[]
): SuggestedRole[] => {
  const result: SuggestedRole[] = [];
  const seen = new Set<string>();
  const normalizeEntry = (entry: Record<string, unknown> | null | undefined): SuggestedRole | null => {
    if (!entry || typeof entry !== 'object') return null;
    const roleName = firstString((entry as { role?: unknown }).role ?? (entry as { name?: unknown }).name ?? (entry as { title?: unknown }).title);
    if (!roleName) return null;
    const fitScoreRaw = (entry as { fit_score?: unknown }).fit_score;
    const fitScore = typeof fitScoreRaw === 'number' ? Math.max(0, Math.min(100, fitScoreRaw)) : undefined;
    const matchedSkills = toUniqueStringArray(
      (entry as { matched_skills?: unknown }).matched_skills
      ?? (entry as { skills?: unknown }).skills
      ?? (entry as { fit_by_skills?: unknown }).fit_by_skills,
    );
    const reasonParts: string[] = [];
    const preferenceFlag = Boolean((entry as { preference?: unknown }).preference);
    const rawReason = firstString((entry as { reason?: unknown }).reason);
    if (rawReason) reasonParts.push(rawReason);
    if (matchedSkills.length) {
      reasonParts.push(`Encaje por skills: ${matchedSkills.join(', ')}`);
    }
    if (typeof fitScore === 'number') {
      reasonParts.push(`Encaje ${Math.round(fitScore)} / 100`);
    }
    if (preferenceFlag) {
      reasonParts.push('Preferencia declarada por el candidato');
    }
    const seniority = firstString((entry as { seniority?: unknown }).seniority ?? (entry as { level?: unknown }).level ?? jobPreferences.seniority);
    const workMode = firstString((entry as { work_mode?: unknown }).work_mode ?? (entry as { modality?: unknown }).modality);
    const remoteFromWorkMode = ['remoto', 'remote', 'teletrabajo', '100% remoto', 'fully remote'].some((flag) => workMode.toLowerCase().includes(flag));
    const remote_viable = typeof (entry as { remote_viable?: unknown }).remote_viable === 'boolean'
      ? Boolean((entry as { remote_viable?: unknown }).remote_viable)
      : remoteFromWorkMode || (jobPreferences.work_mode ? jobPreferences.work_mode.toLowerCase().includes('remoto') : false);
    const reason = reasonParts.filter(Boolean).join(' — ') || 'Propuesto según coincidencia de perfil';
    const signature = `${roleName.toLowerCase()}|${seniority.toLowerCase()}|${remote_viable}`;
    if (seen.has(signature)) return null;
    seen.add(signature);
    return { role: roleName, reason, seniority, remote_viable, fit_score: fitScore }; 
  };
  for (const source of sources) {
    if (!source) continue;
    if (Array.isArray(source)) {
      for (const entry of source) {
        const normalized = normalizeEntry((entry ?? null) as Record<string, unknown> | null);
        if (normalized) result.push(normalized);
      }
    } else if (typeof source === 'object') {
      const maybeArray = (source as { suggested_roles?: unknown }).suggested_roles;
      if (Array.isArray(maybeArray)) {
        for (const entry of maybeArray) {
          const normalized = normalizeEntry((entry ?? null) as Record<string, unknown> | null);
          if (normalized) result.push(normalized);
        }
      } else {
        const normalized = normalizeEntry(source as Record<string, unknown>);
        if (normalized) result.push(normalized);
      }
    }
  }
  return result;
};

const pickBestCvArray = (candidateInput: unknown, priority: ReadonlyArray<string>): CvItem[] => {
  const candidates = Array.isArray(candidateInput) ? candidateInput : [candidateInput];
  const ranked = candidates
    .map((candidate) => {
      const normalized = toCvItemArray(candidate, priority);
      if (!normalized.length) return null;
      const richness = normalized.reduce((acc, item) => {
        return acc + ['title', 'subtitle', 'period', 'level', 'detail'].reduce((score, key) => {
          return score + ((item as Record<string, unknown>)[key] ? 1 : 0);
        }, 0);
      }, 0);
      return { items: normalized, score: richness + normalized.length };
    })
    .filter((entry): entry is { items: CvItem[]; score: number } => Boolean(entry))
    .sort((a, b) => b.score - a.score);
  const merged: CvItem[] = [];
  const seen = new Set<string>();
  for (const candidate of ranked) {
    for (const item of candidate.items) {
      const signature = cvItemSignature(item);
      if (signature && seen.has(signature)) continue;
      seen.add(signature);
      merged.push(item);
    }
  }
  return merged;
};

const buildCvDetails = (sources: Partial<Record<keyof CvDetails, unknown>>): CvDetails => {
  const details: CvDetails = {
    experience: pickBestCvArray(sources.experience, detailPriority.experience),
    education: pickBestCvArray(sources.education, detailPriority.education),
    languages: pickBestCvArray(sources.languages, detailPriority.languages),
    tools: pickBestCvArray(sources.tools, detailPriority.tools),
  };
  if (details.education.length && details.experience.length) {
    const experienceSignatures = new Set(details.experience.map(cvItemSignature).filter(Boolean));
    const experienceText = details.experience
      .map((entry) => [entry.title, entry.subtitle, entry.detail].map((part) => (part || '').toLowerCase().trim()).filter(Boolean).join(' '))
      .filter(Boolean);
    details.education = details.education.filter((entry) => {
      const signature = cvItemSignature(entry);
      if (signature && experienceSignatures.has(signature)) return false;
      const text = [entry.title, entry.subtitle, entry.detail]
        .map((part) => (part || '').toLowerCase().trim())
        .filter(Boolean)
        .join(' ');
      if (!text) return true;
      return !experienceText.some((exp) => exp.includes(text) || text.includes(exp));
    });
  }
  return details;
};

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
        experience: [
          rawDetails.experience,
          rawDetails.experience_highlights,
          data.cv_analysis?.experience,
          data.cv_analysis?.experience_detailed,
        ],
        education: [
          rawDetails.education,
          data.cv_analysis?.education,
          data.cv_analysis?.education_detailed,
        ],
        languages: [rawDetails.languages, data.cv_analysis?.languages],
        tools: [
          rawDetails.tools,
          rawDetails.software,
          data.cv_analysis?.tools,
          data.cv_analysis?.software,
        ],
      });
      const profileSummary = ensureText(data.profile_summary, 'Perfil profesional en desarrollo.');
      const cvSummary = ensureText(data.cv_analysis_summary || data.cv_summary, profileSummary);
      const jsa = {
        cv_optimization: Array.isArray(data?.job_search_advice?.cv_optimization) ? data.job_search_advice.cv_optimization : [],
        letters_portfolio: Array.isArray(data?.job_search_advice?.letters_portfolio)
          ? data.job_search_advice.letters_portfolio
          : (data?.job_search_advice?.letters_portfolio ? [String(data.job_search_advice.letters_portfolio)] : []),
        recommended_platforms: Array.isArray(data?.job_search_advice?.recommended_platforms) ? data.job_search_advice.recommended_platforms : [],
        networking: Array.isArray(data?.job_search_advice?.networking)
          ? data.job_search_advice.networking
          : (data?.job_search_advice?.networking ? [String(data.job_search_advice.networking)] : []),
        interview_tips: Array.isArray(data?.job_search_advice?.interview_tips)
          ? data.job_search_advice.interview_tips
          : (data?.job_search_advice?.interview_tips ? [String(data.job_search_advice.interview_tips)] : []),
      };
      const suggested_roles = normalizeSuggestedRoles(
        normalizedJobPrefs,
        data.suggested_roles,
        data.cv_analysis?.suggested_roles,
        data.cv_analysis,
      );
      const rp = (data.ready_phrases || {}) as any;
      const ready_phrases: ReadyPhrases = {
        headline: String(rp.headline || ''),
        about_me: String(rp.about_me || ''),
        short_message: String(rp.short_message || ''),
      };
      return {
        ...data,
        summary: ensureText(data.summary, profileSummary),
        profile_summary: profileSummary,
        cv_analysis_summary: cvSummary,
        cv_details: normalizedDetails,
        suggested_roles,
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
        job_search_advice: jsa,
        useful_tools: data.useful_tools || { productivity: [], job_search: [], learning: [], accessibility: [] },
        ready_phrases,
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
        letters_portfolio: Array.isArray(report?.job_search_advice?.letters_portfolio)
          ? report.job_search_advice.letters_portfolio
          : (report?.job_search_advice?.letters_portfolio ? [String(report.job_search_advice.letters_portfolio)] : []),
        recommended_platforms: reportRecommendedPlatforms && reportRecommendedPlatforms.length > 0
          ? reportRecommendedPlatforms
          : jobPreferences.preferred_platforms,
        networking: Array.isArray(report?.job_search_advice?.networking)
          ? report.job_search_advice.networking
          : (report?.job_search_advice?.networking ? [String(report.job_search_advice.networking)] : []),
        interview_tips: Array.isArray(report?.job_search_advice?.interview_tips)
          ? report.job_search_advice.interview_tips
          : (report?.job_search_advice?.interview_tips ? [String(report.job_search_advice.interview_tips)] : []),
      };
      // Herramientas
      const useful_tools = {
        productivity: Array.isArray(report?.tools?.productivity) ? report.tools.productivity.filter(Boolean) : [],
        job_search: Array.isArray(report?.tools?.job_search) ? report.tools.job_search.filter(Boolean) : [],
        learning: Array.isArray(report?.tools?.learning) ? report.tools.learning.filter(Boolean) : [],
        accessibility: Array.isArray(report?.tools?.accessibility) ? report.tools.accessibility.filter(Boolean) : [],
      };
      const rp = (report.ready_phrases || {}) as any;
      const ready_phrases: ReadyPhrases = {
        headline: String(rp.headline || ''),
        about_me: String(rp.about_me || ''),
        short_message: String(rp.short_message || ''),
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
      const suggested_roles = normalizeSuggestedRoles(
        jobPreferences,
        report?.suggested_roles,
        cvA?.suggested_roles,
        analysisJson?.suggested_roles,
        data?.cv_analysis?.suggested_roles,
        data?.cv_analysis,
      );
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
      const cv_analysis_summary = ensureText(recs?.resumen_cv || report?.cv_summary, profile_summary);
      return {
        summary: profile_summary,
        personal_data,
        job_preferences: jobPreferences,
        profile_summary,
        cv_analysis_summary,
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
        ready_phrases,
        employability_score: score ?? 0,
        completed_games,
        final_message,
      };
    }
  }
  throw new Error('Formato de datos desconocido');
}

// Mapeo legible para slugs de minijuegos → títulos en español
export const GAME_NAME_MAP: Record<string, string> = {
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
  'softskills-evaluated': 'Evaluación de habilidades blandas',
};

export function getPrettyGameName(g: string): string {
  return GAME_NAME_MAP[g] ?? g.replace(/-/g, ' ');
}

export function generateNewFormatReport(data: NewReportSchema): string {
  const prettyGames = (data.completed_games || []).map((g) => getPrettyGameName(g));
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
  const cvItemToString = (item: CvItem): string => {
    const parts = [item.title, item.subtitle, item.period, item.level, item.detail].filter(Boolean);
    return parts.join(' — ');
  };
  const addDetailSection = (title: string, items?: CvItem[]): void => {
    if (!items || items.length === 0) return;
    const normalized = items
      .map((item) => cvItemToString(item))
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
    data.cv_analysis_summary,
    ...detailSectionLines,
    '## 5. Fortalezas',
    ...data.strengths.map((s) => `- ${s}`),
    '',
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
    'Cartas y portafolio:',
    ...data.job_search_advice.letters_portfolio.map((tip) => `- ${tip}`),
    `Plataformas recomendadas: ${data.job_search_advice.recommended_platforms.join(', ')}`,
    'Networking:',
    ...data.job_search_advice.networking.map((tip) => `- ${tip}`),
    'Entrevistas:',
    ...data.job_search_advice.interview_tips.map((tip) => `- ${tip}`),
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
    '',
    '## 14. Frases listas (para copiar y pegar)',
    `**Titular:** ${data.ready_phrases?.headline || ''}`,
    `**Acerca de:** ${data.ready_phrases?.about_me || ''}`,
    `**Mensaje corto:** ${data.ready_phrases?.short_message || ''}`,
  ];
  return lines.join('\n');
}