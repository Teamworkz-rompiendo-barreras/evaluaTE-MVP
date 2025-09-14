"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);
var reportConfig_exports = {};
__export(reportConfig_exports, {
  convertBackendResponseToNewFormat: () => convertBackendResponseToNewFormat,
  generateNewFormatReport: () => generateNewFormatReport
});
module.exports = __toCommonJS(reportConfig_exports);
function convertBackendResponseToNewFormat(raw) {
  if (raw && typeof raw === "object") {
    const data = raw;
    // Ya en formato nuevo
    if (data.summary && data.personal_data) {
      return data;
    }
    // Conversión desde formato backend actual
    if (data.report) {
      const report = data.report || {};
      const recs = data.recommendations && typeof data.recommendations === 'object' ? data.recommendations : {};

      // Datos personales
      const pdSrc = report.personal_data || {};
      const personal_data = {
        name: String(pdSrc.name ?? report.fullName ?? data.fullName ?? 'Desconocido'),
        location: String(pdSrc.location ?? ''),
        email: String(pdSrc.email ?? ''),
        phone: String(pdSrc.phone ?? ''),
        disability_certificate: String(pdSrc.disability_certificate ?? ''),
      };

      // Análisis CV
      const cvA = report.cv_analysis || {};
      const analysisJson = cvA && typeof cvA === 'object' && cvA.analysis_json && typeof cvA.analysis_json === 'object' ? cvA.analysis_json : {};
      const stars = cvA && typeof cvA === 'object' && cvA.stars && typeof cvA.stars === 'object' ? cvA.stars : {};
      const parseStars = (val) => {
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
        observations: Array.isArray(analysisJson?.observations)
          ? analysisJson.observations.map((o) => String(o))
          : Object.values(analysisJson?.evidence || {}).map((v) => String(v)).filter((v) => v.length > 0),
        actions: Array.isArray(analysisJson?.actions)
          ? analysisJson.actions.map((a) => String(a))
          : [
              ...(Array.isArray(analysisJson?.corrections) ? analysisJson.corrections.map((c) => String(c)) : []),
              ...(Array.isArray(analysisJson?.reordering_suggestions)
                ? analysisJson.reordering_suggestions.map((r) => String(r))
                : []),
            ],
      };

      // Fortalezas
      let strengths = [];
      if (Array.isArray(recs.fortalezas_clave)) {
        strengths = recs.fortalezas_clave.map((s) => String(s));
      } else if (Array.isArray(report.soft_skills)) {
        strengths = report.soft_skills
          .filter((s) => (Number(s?.score) || 0) >= 70)
          .map((s) => String(s?.skill || s?.name || ''));
      }

      // Áreas de mejora
      let improvement_areas = [];
      if (Array.isArray(recs.areas_mejora)) {
        improvement_areas = recs.areas_mejora.map((a) => ({
          area: String(a?.area ?? a ?? ''),
          reason: String(a?.reason ?? ''),
          suggested_action: String(a?.suggested_action ?? ''),
        }));
      } else if (Array.isArray(report.improvement_areas)) {
        improvement_areas = report.improvement_areas.map((a) => ({
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
        ? report.suggested_roles.map((r) => ({
            role: String(r?.role ?? r?.name ?? ''),
            reason: String(r?.reason ?? ''),
            seniority: String(r?.seniority ?? ''),
            remote_viable: Boolean(r?.remote_viable),
          }))
        : [];

      // Otros
      const ideal_work_environment = String(
        recs?.entornos_ideales
          || (Array.isArray(report?.environments) ? report.environments.join(', ') : '')
          || ''
      );
      const completed_games = Array.isArray(report?.completed_games) ? report.completed_games.map(String) : [];
      const final_message = String(recs?.frase_final || report?.frase_final || '');

      const profile_summary = String(recs?.resumen_perfil || report?.resumen_ejecutivo || data?.summary || '');
      const summary = String(report?.resumen_ejecutivo || data?.summary || profile_summary || '');
      const cv_summary = String(recs?.resumen_cv || '');

      return {
        summary,
        personal_data,
        profile_summary,
        cv_summary,
        strengths,
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
  throw new Error("Formato de datos desconocido");
}
function generateNewFormatReport(data) {
  const gameNameMap = {
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
  const prettyGames = (data.completed_games || []).map((g) => gameNameMap[g] || g.replace(/-/g, ' '));
  const lines = [
    "## 1. Datos personales básicos",
    `Nombre: ${data.personal_data.name}`,
    `Ubicación: ${data.personal_data.location}`,
    `Email: ${data.personal_data.email}`,
    `Teléfono: ${data.personal_data.phone}`,
    "",
    "## 2. Resumen del perfil",
    data.profile_summary,
    "",
    "## 3. Resumen del CV",
    data.cv_summary,
    "",
    "## 4. Fortalezas",
    ...data.strengths.map((s) => `- ${s}`),
    "",
    "# 5. Áreas de mejora y consejos",
    ...data.improvement_areas.map((a) => `- ${a.area} - ${a.reason}${a.suggested_action ? ` (Acción: ${a.suggested_action})` : ""}`),
    "",
    "## 6. Análisis del CV con puntuación 1–5",
    `Estructura: ${data.cv_analysis.structure_score}/5`,
    `Coherencia: ${data.cv_analysis.coherence_score}/5`,
    `Información clave: ${data.cv_analysis.key_info_score}/5`,
    `Claridad: ${data.cv_analysis.clarity_score}/5`,
    `Estilo: ${data.cv_analysis.style_score}/5`,
    "",
    "Observaciones del análisis:",
    ...data.cv_analysis.observations.map((o) => `- ${o}`),
    "",
    "Correcciones/Acciones:",
    ...data.cv_analysis.actions.map((a) => `- ${a}`),
    "",
    "## 7. Entornos de trabajo ideales",
    data.ideal_work_environment,
    "",
    "## 8. Roles profesionales sugeridos",
    ...data.suggested_roles.map((r) => `- ${r.role} - ${r.reason}`),
    "",
    "## 9. Plan de acción",
    "Corto plazo:",
    ...data.action_plan.short_term.map((s) => `- ${s}`),
    "Mediano plazo:",
    ...data.action_plan.medium_term.map((s) => `- ${s}`),
    "Largo plazo:",
    ...data.action_plan.long_term.map((s) => `- ${s}`),
    "",
    "## 10. Consejos de búsqueda de empleo",
    "Optimización del CV:",
    ...data.job_search_advice.cv_optimization.map((tip) => `- ${tip}`),
    `Cartas y portafolio: ${data.job_search_advice.letters_portfolio}`,
    `Plataformas recomendadas: ${data.job_search_advice.recommended_platforms.join(", ")}`,
    `Networking: ${data.job_search_advice.networking}`,
    `Entrevistas: ${data.job_search_advice.interview_tips}`,
    "",
    "## 11. Herramientas útiles y tecnología",
    `Productividad: ${data.useful_tools.productivity.join(", ")}`,
    `Búsqueda de empleo: ${data.useful_tools.job_search.join(", ")}`,
    `Aprendizaje: ${data.useful_tools.learning.join(", ")}`,
    `Accesibilidad: ${data.useful_tools.accessibility.join(", ")}`,
    "",
    "## 12. Juegos completados",
    ...prettyGames.map((g) => `- ${g}`),
    "",
    "## 13. Frase final de cierre",
    data.final_message
  ];
  return lines.join("\n");
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  convertBackendResponseToNewFormat,
  generateNewFormatReport
});
