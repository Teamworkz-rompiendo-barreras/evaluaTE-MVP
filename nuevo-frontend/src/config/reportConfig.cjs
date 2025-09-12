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
  var _a, _b;
  if (raw && typeof raw === "object") {
    const data = raw;
    if (data.summary && data.personal_data) {
      return data;
    }
    if (data.report) {
      const report = data.report || {};
      return {
        summary: report.resumen_ejecutivo || "",
        personal_data: {
          name: report.fullName || "Desconocido",
          location: report.location || "",
          email: report.email || "",
          phone: report.phone || "",
          disability_certificate: ""
        },
        profile_summary: report.resumen_ejecutivo || "",
        cv_summary: ((_a = report.cvAnalysis) == null ? void 0 : _a.feedback) || "",
        strengths: Array.isArray(data.recommendations) ? data.recommendations : [],
        improvement_areas: [],
        cv_analysis: {
          structure_score: 0,
          coherence_score: 0,
          key_info_score: 0,
          clarity_score: 0,
          style_score: 0,
          evidence: {
            structure: ((_b = report.cvAnalysis) == null ? void 0 : _b.structure) || "",
            coherence: "",
            key_info: "",
            clarity: "",
            style: ""
          },
          corrections: [],
          reordering_suggestions: []
        },
        ideal_work_environment: "",
        suggested_roles: [],
        action_plan: { short_term: [], medium_term: [], long_term: [] },
        job_search_advice: {
          cv_optimization: [],
          letters_portfolio: "",
          recommended_platforms: [],
          networking: "",
          interview_tips: ""
        },
        useful_tools: {
          productivity: [],
          job_search: [],
          learning: [],
          accessibility: []
        },
        completed_games: [],
        final_message: ""
      };
    }
  }
  throw new Error("Formato de datos desconocido");
}
function generateNewFormatReport(data) {
  const lines = [
    "1. DATOS PERSONALES B\xC1SICOS",
    `Nombre: ${data.personal_data.name}`,
    `Ubicaci\xF3n: ${data.personal_data.location}`,
    `Email: ${data.personal_data.email}`,
    `Tel\xE9fono: ${data.personal_data.phone}`,
    "",
    "2. RESUMEN DEL PERFIL",
    data.profile_summary,
    "",
    "3. RESUMEN DEL CV",
    data.cv_summary,
    "",
    "4. FORTALEZAS",
    ...data.strengths.map((s, i) => `${i + 1}. ${s}`),
    "",
    "5. \xC1REAS DE MEJORA Y CONSEJOS",
    ...data.improvement_areas.map(
      (a, i) => `${i + 1}. ${a.area} - ${a.reason}${a.suggested_action ? ` (Acci\xF3n: ${a.suggested_action})` : ""}`
    ),
    "",
    "6. AN\xC1LISIS DEL CV CON PUNTUACI\xD3N 1\u20135",
    `Estructura: ${data.cv_analysis.structure_score}/5`,
    `Coherencia: ${data.cv_analysis.coherence_score}/5`,
    `Informaci\xF3n clave: ${data.cv_analysis.key_info_score}/5`,
    `Claridad: ${data.cv_analysis.clarity_score}/5`,
    `Estilo: ${data.cv_analysis.style_score}/5`,
    "",
    "7. ENTORNOS DE TRABAJO IDEALES",
    data.ideal_work_environment,
    "",
    "8. ROLES PROFESIONALES SUGERIDOS",
    ...data.suggested_roles.map((r, i) => `${i + 1}. ${r.role} - ${r.reason}`),
    "",
    "9. PLAN DE ACCI\xD3N",
    "Corto plazo:",
    ...data.action_plan.short_term.map((s, i) => `${i + 1}. ${s}`),
    "Mediano plazo:",
    ...data.action_plan.medium_term.map((s, i) => `${i + 1}. ${s}`),
    "Largo plazo:",
    ...data.action_plan.long_term.map((s, i) => `${i + 1}. ${s}`),
    "",
    "10. CONSEJOS DE B\xDASQUEDA DE EMPLEO",
    "Optimizaci\xF3n del CV:",
    ...data.job_search_advice.cv_optimization.map((tip, i) => `${i + 1}. ${tip}`),
    `Cartas y portafolio: ${data.job_search_advice.letters_portfolio}`,
    `Plataformas recomendadas: ${data.job_search_advice.recommended_platforms.join(", ")}`,
    `Networking: ${data.job_search_advice.networking}`,
    `Entrevistas: ${data.job_search_advice.interview_tips}`,
    "",
    "11. HERRAMIENTAS \xDATILES Y TECNOLOG\xCDA",
    `Productividad: ${data.useful_tools.productivity.join(", ")}`,
    `B\xFAsqueda de empleo: ${data.useful_tools.job_search.join(", ")}`,
    `Aprendizaje: ${data.useful_tools.learning.join(", ")}`,
    `Accesibilidad: ${data.useful_tools.accessibility.join(", ")}`,
    "",
    "12. JUEGOS COMPLETADOS",
    ...data.completed_games.map((g, i) => `${i + 1}. ${g}`),
    "",
    "13. FRASE FINAL DE CIERRE",
    data.final_message
  ];
  return lines.join("\n");
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  convertBackendResponseToNewFormat,
  generateNewFormatReport
});
