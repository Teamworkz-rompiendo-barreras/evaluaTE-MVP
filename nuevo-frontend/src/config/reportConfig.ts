import type { CvAnalysis } from '@/types/report';

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
      return {
        summary: report.resumen_ejecutivo || '',
        personal_data: {
          name: report.fullName || 'Desconocido',
          location: '',
          email: '',
          phone: '',
          disability_certificate: ''
        },
        profile_summary: report.resumen_ejecutivo || '',
        cv_summary: report.cvAnalysis?.feedback || '',
        strengths: Array.isArray(data.recommendations) ? data.recommendations : [],
        improvement_areas: [],
        cv_analysis: {
          structure_score: 0,
          coherence_score: 0,
          key_info_score: 0,
          clarity_score: 0,
          style_score: 0,
          evidence: {
            structure: report.cvAnalysis?.structure || '',
            coherence: '',
            key_info: '',
            clarity: '',
            style: ''
          },
          corrections: [],
          reordering_suggestions: []
        },
        ideal_work_environment: '',
        suggested_roles: [],
        action_plan: { short_term: [], medium_term: [], long_term: [] },
        job_search_advice: {
          cv_optimization: [],
          letters_portfolio: '',
          recommended_platforms: [],
          networking: '',
          interview_tips: ''
        },
        useful_tools: {
          productivity: [],
          job_search: [],
          learning: [],
          accessibility: []
        },
        completed_games: [],
        final_message: ''
      };
    }
  }
  throw new Error('Formato de datos desconocido');
}

export function generateNewFormatReport(data: NewReportSchema): string {
  const lines = [
    '1. DATOS PERSONALES BÁSICOS',
    `Nombre: ${data.personal_data.name}`,
    `Ubicación: ${data.personal_data.location}`,
    `Email: ${data.personal_data.email}`,
    `Teléfono: ${data.personal_data.phone}`,
    '',
    '2. RESUMEN DEL PERFIL',
    data.profile_summary,
    '',
    '3. RESUMEN DEL CV',
    data.cv_summary,
    '',
    '4. FORTALEZAS',
    ...data.strengths.map((s, i) => `${i + 1}. ${s}`),
    '',
    '5. ÁREAS DE MEJORA Y CONSEJOS',
    ...data.improvement_areas.map(
      (a, i) => `${i + 1}. ${a.area} - ${a.reason}${a.suggested_action ? ` (Acción: ${a.suggested_action})` : ''}`
    ),
    '',
    '6. ANÁLISIS DEL CV CON PUNTUACIÓN 1–5',
    `Estructura: ${data.cv_analysis.structure_score}/5`,
    `Coherencia: ${data.cv_analysis.coherence_score}/5`,
    `Información clave: ${data.cv_analysis.key_info_score}/5`,
    `Claridad: ${data.cv_analysis.clarity_score}/5`,
    `Estilo: ${data.cv_analysis.style_score}/5`,
    '',
    '7. ENTORNOS DE TRABAJO IDEALES',
    data.ideal_work_environment,
    '',
    '8. ROLES PROFESIONALES SUGERIDOS',
    ...data.suggested_roles.map((r, i) => `${i + 1}. ${r.role} - ${r.reason}`),
    '',
    '9. PLAN DE ACCIÓN',
    'Corto plazo:',
    ...data.action_plan.short_term.map((s, i) => `${i + 1}. ${s}`),
    'Mediano plazo:',
    ...data.action_plan.medium_term.map((s, i) => `${i + 1}. ${s}`),
    'Largo plazo:',
    ...data.action_plan.long_term.map((s, i) => `${i + 1}. ${s}`),
    '',
    '10. CONSEJOS DE BÚSQUEDA DE EMPLEO',
    'Optimización del CV:',
    ...data.job_search_advice.cv_optimization.map((tip, i) => `${i + 1}. ${tip}`),
    `Cartas y portafolio: ${data.job_search_advice.letters_portfolio}`,
    `Plataformas recomendadas: ${data.job_search_advice.recommended_platforms.join(', ')}`,
    `Networking: ${data.job_search_advice.networking}`,
    `Entrevistas: ${data.job_search_advice.interview_tips}`,
    '',
    '11. HERRAMIENTAS ÚTILES Y TECNOLOGÍA',
    `Productividad: ${data.useful_tools.productivity.join(', ')}`,
    `Búsqueda de empleo: ${data.useful_tools.job_search.join(', ')}`,
    `Aprendizaje: ${data.useful_tools.learning.join(', ')}`,
    `Accesibilidad: ${data.useful_tools.accessibility.join(', ')}`,
    '',
    '12. JUEGOS COMPLETADOS',
    ...data.completed_games.map((g, i) => `${i + 1}. ${g}`),
    '',
    '13. FRASE FINAL DE CIERRE',
    data.final_message
  ];

  return lines.join('\n');
}
