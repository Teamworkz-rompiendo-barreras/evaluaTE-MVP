// Utility functions to handle the new report format used on the front-end.
// These helpers convert legacy backend responses to the new structure and
// generate a markdown report from that structure.

function convertBackendResponseToNewFormat(data) {
  if (!data || typeof data !== 'object') {
    return {
      summary: '',
      personal_data: {},
      profile_summary: '',
      cv_summary: '',
      strengths: [],
      improvement_areas: [],
      cv_analysis: {},
      ideal_work_environment: '',
      suggested_roles: [],
      action_plan: {},
      job_search_advice: {},
      useful_tools: {},
      completed_games: [],
      final_message: ''
    };
  }

  // If the response already follows the new structure, clone it to avoid
  // accidental mutations and return.
  if (data.personal_data || data.profile_summary || data.cv_summary) {
    return JSON.parse(JSON.stringify(data));
  }

  const r = data.report || {};

  return {
    summary: data.summary || r.resumen_ejecutivo || '',
    personal_data: {
      name: r.fullName || '',
      location: r.location || '',
      email: r.email || '',
      phone: r.phone || '',
      disability_certificate: r.disability_certificate || ''
    },
    profile_summary: r.resumen_ejecutivo || data.profile_summary || '',
    cv_summary:
      r.cvSummary ||
      (r.cvAnalysis && (r.cvAnalysis.feedback || r.cvAnalysis.summary)) ||
      data.cv_summary ||
      '',
    strengths: r.strengths || data.recommendations || [],
    improvement_areas: r.improvement_areas || data.improvement_areas || [],
    cv_analysis: r.cv_analysis || r.cvAnalysis || data.cv_analysis || {},
    ideal_work_environment: data.ideal_work_environment || r.ideal_work_environment || '',
    suggested_roles: data.suggested_roles || r.suggested_roles || [],
    action_plan: data.action_plan || r.action_plan || {},
    job_search_advice: data.job_search_advice || r.job_search_advice || {},
    useful_tools: data.useful_tools || r.useful_tools || {},
    completed_games: data.completed_games || r.completed_games || [],
    final_message: data.final_message || r.frase_final || ''
  };
}

function generateNewFormatReport(info) {
  const lines = ['# Informe Profesional de Empleabilidad', ''];

  const pd = info.personal_data || {};
  lines.push('1. DATOS PERSONALES BÁSICOS');
  lines.push(`- **Nombre**: ${pd.name || 'No disponible'}`);
  lines.push(`- **Ubicación**: ${pd.location || 'No disponible'}`);
  lines.push(`- **Email**: ${pd.email || 'No disponible'}`);
  lines.push(`- **Teléfono**: ${pd.phone || 'No disponible'}`);
  lines.push(`- **Certificado de discapacidad**: ${pd.disability_certificate || 'No indicado'}`);
  lines.push('');

  lines.push('2. RESUMEN DEL PERFIL');
  lines.push(info.profile_summary || info.summary || 'No disponible');
  lines.push('');

  lines.push('3. RESUMEN DEL CV');
  lines.push(info.cv_summary || 'No disponible');
  lines.push('');

  lines.push('4. FORTALEZAS');
  if (Array.isArray(info.strengths) && info.strengths.length) {
    info.strengths.forEach(s => lines.push(`- ${s}`));
  } else {
    lines.push('- No especificadas');
  }
  lines.push('');

  lines.push('5. ÁREAS DE MEJORA Y CONSEJOS');
  if (Array.isArray(info.improvement_areas) && info.improvement_areas.length) {
    info.improvement_areas.forEach(a => {
      if (typeof a === 'string') {
        lines.push(`- ${a}`);
      } else {
        const reason = a.reason ? ` (${a.reason})` : '';
        const action = a.suggested_action ? ` → ${a.suggested_action}` : '';
        lines.push(`- ${a.area || ''}${reason}${action}`);
      }
    });
  } else {
    lines.push('- No especificadas');
  }
  lines.push('');

  const ca = info.cv_analysis || {};
  lines.push('6. ANÁLISIS DEL CV CON PUNTUACIÓN 1–5');
  lines.push(`- Formato: ${ca.structure_score ?? 'N/D'}`);
  lines.push(`- Claridad: ${ca.clarity_score ?? 'N/D'}`);
  lines.push(`- Coherencia: ${ca.coherence_score ?? 'N/D'}`);
  lines.push(`- Información clave: ${ca.key_info_score ?? 'N/D'}`);
  lines.push(`- Ortografía y estilo: ${ca.style_score ?? ca.spelling_style_score ?? 'N/D'}`);
  if (Array.isArray(ca.corrections) && ca.corrections.length) {
    lines.push('  Correcciones sugeridas:');
    ca.corrections.forEach(c => lines.push(`  - ${c}`));
  }
  lines.push('');

  lines.push('7. ENTORNOS DE TRABAJO IDEALES');
  lines.push(info.ideal_work_environment || 'No especificado');
  lines.push('');

  lines.push('8. ROLES PROFESIONALES SUGERIDOS');
  if (Array.isArray(info.suggested_roles) && info.suggested_roles.length) {
    info.suggested_roles.forEach(r => {
      if (typeof r === 'string') {
        lines.push(`- ${r}`);
      } else {
        const reason = r.reason ? ` — ${r.reason}` : '';
        lines.push(`- ${r.role || r.name || ''}${reason}`);
      }
    });
  } else {
    lines.push('- No especificados');
  }
  lines.push('');

  lines.push('9. PLAN DE ACCIÓN');
  const ap = info.action_plan || {};
  const addPlan = (arr, title) => {
    if (Array.isArray(arr) && arr.length) {
      lines.push(`- ${title}:`);
      arr.forEach(it => lines.push(`  - ${it}`));
    }
  };
  if (ap.short_term || ap.medium_term || ap.long_term) {
    addPlan(ap.short_term, 'Corto plazo');
    addPlan(ap.medium_term, 'Medio plazo');
    addPlan(ap.long_term, 'Largo plazo');
  } else {
    lines.push('- No especificado');
  }
  lines.push('');

  lines.push('10. CONSEJOS DE BÚSQUEDA DE EMPLEO');
  const js = info.job_search_advice || {};
  if (Array.isArray(js.cv_optimization)) {
    lines.push('**Optimización del CV**');
    js.cv_optimization.forEach(t => lines.push(`- ${t}`));
  }
  if (js.letters_portfolio) {
    lines.push('**Cartas y portfolio**');
    lines.push(js.letters_portfolio);
  }
  if (Array.isArray(js.recommended_platforms)) {
    lines.push('**Plataformas recomendadas**');
    js.recommended_platforms.forEach(p => lines.push(`- ${p}`));
  }
  if (js.networking) {
    lines.push('**Networking**');
    lines.push(js.networking);
  }
  if (js.interview_tips) {
    lines.push('**Entrevistas**');
    lines.push(js.interview_tips);
  }
  if (!js.cv_optimization && !js.letters_portfolio && !js.recommended_platforms && !js.networking && !js.interview_tips) {
    lines.push('- No especificado');
  }
  lines.push('');

  lines.push('11. HERRAMIENTAS ÚTILES Y TECNOLOGÍA');
  const ut = info.useful_tools || {};
  const printTools = (arr, title) => {
    if (Array.isArray(arr) && arr.length) {
      lines.push(`**${title}**`);
      arr.forEach(t => lines.push(`- ${t}`));
    }
  };
  printTools(ut.productivity, 'Productividad');
  printTools(ut.job_search, 'Búsqueda de empleo');
  printTools(ut.learning, 'Aprendizaje');
  printTools(ut.accessibility, 'Accesibilidad');
  if (!ut.productivity && !ut.job_search && !ut.learning && !ut.accessibility) {
    lines.push('- No especificado');
  }
  lines.push('');

  lines.push('12. JUEGOS COMPLETADOS');
  if (Array.isArray(info.completed_games) && info.completed_games.length) {
    info.completed_games.forEach(g => lines.push(`- ${g}`));
  } else {
    lines.push('- No especificados');
  }
  lines.push('');

  lines.push('13. FRASE FINAL DE CIERRE');
  lines.push(info.final_message || info.closing_statement || '');
  lines.push('');
  lines.push('*Informe generado automáticamente.*');

  return lines.join('\n');
}

export { convertBackendResponseToNewFormat, generateNewFormatReport };
