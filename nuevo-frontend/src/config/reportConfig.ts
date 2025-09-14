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

export interface NewReportSchema {
  summary: string;
  personal_data: PersonalData;
  profile_summary: string;
  cv_summary: string;
  strengths: string[];
  soft_skills: Array<{ skill: string; score: number }>;
  improvement_areas: ImprovementArea[];
  cv_analysis: CvAnalysis;
  ideal_work_environment: string;
  suggested_roles: SuggestedRole[];
  action_plan: ActionPlan;
  job_search_advice: JobSearchAdvice;
  useful_tools: UsefulTools;
  completed_games: string[];
  final_message: string;
}

export function convertBackendResponseToNewFormat(raw: unknown): NewReportSchema {
  if (raw && typeof raw === 'object') {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const data: any = raw;
    // Already in new format
    if (data.summary && data.personal_data) {
      return data as NewReportSchema;
    }
    // Old format conversion
    if (data.report) {
      const report = data.report || {};
      const recs = (data.recommendations && typeof data.recommendations === 'object') ? data.recommendations : {};

      // Personal data: preferir report.personal_data si existe
      const pdSrc = report.personal_data || {};
      const personal_data = {
        name: String(pdSrc.name ?? report.fullName ?? data.fullName ?? 'Desconocido'),
        location: String(pdSrc.location ?? ''),
        email: String(pdSrc.email ?? ''),
        phone: String(pdSrc.phone ?? ''),
        disability_certificate: String(pdSrc.disability_certificate ?? ''),
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
        productivity: Array.isArray(report?.tools?.productivity) ? report.tools.productivity : [],
        job_search: Array.isArray(report?.tools?.job_search) ? report.tools.job_search : [],
        learning: Array.isArray(report?.tools?.learning) ? report.tools.learning : [],
        accessibility: Array.isArray(report?.tools?.accessibility) ? report.tools.accessibility : [],
      };

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

      return {
        summary,
        personal_data,
        profile_summary,
        cv_summary,
        strengths,
        soft_skills,
        improvement_areas,
        cv_analysis,
        ideal_work_environment,
        suggested_roles,
        action_plan,
        job_search_advice,
        useful_tools,
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
    '',
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
    `Estructura: ${data.cv_analysis.structure_score}/5`,
    `Coherencia: ${data.cv_analysis.coherence_score}/5`,
    `Información clave: ${data.cv_analysis.key_info_score}/5`,
    `Claridad: ${data.cv_analysis.clarity_score}/5`,
    `Estilo: ${data.cv_analysis.style_score}/5`,
    '',
    '## 7. Entornos de trabajo ideales',
    data.ideal_work_environment,
    '',
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
    `Productividad: ${data.useful_tools.productivity.join(', ')}`,
    `Búsqueda de empleo: ${data.useful_tools.job_search.join(', ')}`,
    `Aprendizaje: ${data.useful_tools.learning.join(', ')}`,
    `Accesibilidad: ${data.useful_tools.accessibility.join(', ')}`,
    '',
    '## 12. Juegos completados',
    ...prettyGames.map((g) => `- ${g}`),
    '',
    '## 13. Frase final de cierre',
    data.final_message,
  ];

  return lines.join('\n');
}
