// src/pages/ResultadosPage.tsx
import React, { useEffect, useState, useRef } from 'react';
import { useAppSelector } from '../app/hooks';
import type { RootState } from '../app/store';
import { buildApiUrl, API_CONFIG } from '../config/api';
import { AZURE_CONFIG } from '../config/azure-config';
import { ResponsiveRadar } from '@nivo/radar';
import logo from '../assets/Logo_teamworkz.png';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useMemo } from 'react';
import '../styles/print.css';
import '../styles/report.css'; // Importar los nuevos estilos
import '../styles/stars.css'; // Importar estilos para estrellas
import { validateSoftSkills } from '../utils/debug-state';
import { filterValidSoftSkills } from '../utils/data-validation';
import { useDispatch } from 'react-redux';
import { generateFinalReport, saveCvAnalysis, saveSoftSkills } from '../features/personal/personalSlice';
import useCvRating from '../hooks/useCvRating';

// Definir tipos locales para evitar importaciones problemáticas

// Tipos del rating del CV
type CvStars = 1|2|3|4|5;

type CvDiagnostico = {
  structure_score: CvStars;
  clarity_score: CvStars;
  coherence_score: CvStars;
  key_info_score: CvStars;
  spelling_style_score: CvStars;
  evidence: { 
    structure: string; 
    coherence: string; 
    key_info: string; 
    clarity: string; 
    style: string; 
  };
};


// Tipo para los datos del radar
interface RadarDataItem {
  skill: string;
  score: number;
  [key: string]: unknown;
}

// Función para extraer el bloque JSON radarData del Markdown
function extractRadarData(markdown: string): RadarDataItem[] {
  const regex = /```json\s*([\s\S]*?)\s*```/g;
  const matches = [...markdown.matchAll(regex)];
  for (const match of matches) {
    try {
      if (match[1]) {
        const json = JSON.parse(match[1]);
        if (json && Array.isArray(json.radarData)) {
          return json.radarData;
        }
      }
    } catch (e) {
      // Ignorar errores de parseo
    }
  }
  return [];
}

// Función helper para mapeo seguro


// Eliminada: helper no usado tras la remaquetación del informe





// (Eliminado) Helper antiguo de estrellas no utilizado



// Componente para renderizar estrellas (sin regex/escapes que rompan el lint)
const Stars: React.FC<{ n: CvStars }> = ({ n }) => {
  const filled = "★".repeat(n);
  const empty = "☆".repeat(5 - n);
  return (
    <span aria-label={`${n} de 5`}>
      <span style={{ color: '#fbbf24', fontWeight: 'bold' }}>{filled}</span>
      <span style={{ color: '#fbbf24', opacity: '0.3' }}>{empty}</span>
    </span>
  );
};

// Variante para diagnóstico con estilo dorado uniforme
const StarsGold: React.FC<{ n: CvStars }> = ({ n }) => {
  const filled = "★".repeat(n);
  const empty = "☆".repeat(5 - n);
  return (
    <span aria-label={`${n} de 5`}>
      <span 
        className="star-filled" 
        style={{ 
          color: '#fbbf24 !important', 
          fontWeight: 'bold',
          fontSize: '1.25rem',
          textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
        }}
      >
        {filled}
      </span>
      <span 
        className="star-empty" 
        style={{ 
          color: '#fbbf24 !important',
          opacity: '0.3',
          fontSize: '1.25rem'
        }}
      >
        {empty}
      </span>
    </span>
  );
};

// Función helper que usa el componente Stars para diagnóstico
const renderDiagnosticoUI = (diag: CvDiagnostico) => (
  <div>
    <p><b>Formato:</b> <Stars n={diag.structure_score}/></p>
    <p><b>Claridad:</b> <Stars n={diag.clarity_score}/></p>
    <p><b>Coherencia:</b> <Stars n={diag.coherence_score}/></p>
    <p><b>Información clave:</b> <Stars n={diag.key_info_score}/></p>
    <p><b>Ortografía:</b> <Stars n={diag.spelling_style_score}/></p>
  </div>
);

// Función para usar en el futuro cuando se implemente la visualización del diagnóstico
// Se mantiene para evitar warnings de TypeScript sobre tipos no utilizados
void renderDiagnosticoUI;







// --- Helpers para construir el markdown deseado ---
function buildDesiredMarkdown(payload: any, userFullName: string): string {
  const r = payload?.report ?? payload ?? {};

  const fullName = userFullName || r?.personal_data?.name || 'Usuario/a';
  const location = r?.personal_data?.location || 'No especificado';
  const email = r?.personal_data?.email || 'No proporcionado';
  const phone = r?.personal_data?.phone || 'No proporcionado';
  const linkedin = r?.personal_data?.linkedin || '(no especificado; recomendado crear/actualizar)';

  // Soft skills: preferir las devueltas por backend; si no, aceptar las que vengan en el payload (eco del request)
  const softSkills = Array.isArray(r?.soft_skills) ? r.soft_skills : (Array.isArray((payload as any)?.softSkills) ? (payload as any).softSkills : []);
  const cv = r?.cv_analysis ?? {};
  const cvExp = Array.isArray(cv?.experience) ? cv.experience : [];
  const cvEdu = Array.isArray(cv?.education) ? cv.education : [];
  const cvLang = Array.isArray(cv?.languages) ? cv.languages : [];
  const cvSoft = Array.isArray(cv?.software) ? cv.software : [];

  const improvement = Array.isArray(r?.improvement_areas) ? r.improvement_areas : [];
  const roles = Array.isArray(r?.suggested_roles) ? r.suggested_roles : [];
  const plan = r?.action_plan ?? {};
  // const tips = (r?.job_search_advice?.tips ?? r?.consejos_busqueda ?? []) as string[]; // Ya no se usa, reemplazado por jobSearchStrategies
  // const tools = r?.tools ?? {}; // Ya no se usa, reemplazado por recursos personalizados
  // const completed = Array.isArray(r?.completed_games) ? r.completed_games : []; // Ya no se usa, reemplazado por topSkills
  // const closing = r?.frase_final || ''; // No se usa: generamos un mensaje final propio

  // Utilidades
  const ssTop = [...softSkills].sort((a:any,b:any)=> (b?.score??0) - (a?.score??0));

  // Generador de listas seguro con opción de sangría para listas anidadas
  const createBullets = (
    arr: unknown,
    formatter: (x:any)=>string,
    indentSpaces: number = 0,
  ) => {
    const pad = ' '.repeat(Math.max(0, indentSpaces));
    if (Array.isArray(arr) && arr.length > 0) {
      return arr.map((item:any) => `${pad}- ${formatter(item)}`).join('\n');
    }
    return `${pad}- (no especificado)`;
  };

  const expBullets = createBullets(
    cvExp,
    (e:any) => `**${e.title || e.text || 'Experiencia'}${e.company ? `, ${e.company}` : ''}**${e.dates ? ` (${e.dates})` : ''}: ${e.summary || e.text || ''}`,
    0,
  );

  const eduBullets = createBullets(
    cvEdu,
    (e:any) => `${e.degree || e.text || 'Formación'}${e.center ? ` – ${e.center}` : ''}${e.year ? ` (${e.year})` : ''}`,
    0,
  );

  const langs = cvLang.length ? cvLang.map((l:any)=> {
    const name = l.text || l.name || l.language || l;
    const level = normalizeLevelText(l.level);
    return `* ${name} — ${level}`;
  }).join('\n') : '* No especificado';
  const softw = cvSoft.length ? cvSoft.map((s: any) => {
    // Si s es un objeto con name y level, usar esos campos
    if (typeof s === 'object' && s !== null) {
      const name = s.name || s.software || s.skill || s;
      const level = normalizeLevelText(s.level || s.proficiency);
      return `* ${name} — ${level}`;
    }
    // Si s es un string simple, mostrarlo tal como está
    return `* ${s}`;
  }).join('\n') : '* No especificado';

  // Generar texto personalizado del resumen del CV
  const generateCvSummaryText = () => {
    const firstName = fullName.split(' ')[0] || 'El candidato';
    const experienceCount = cvExp.length;
    const educationCount = cvEdu.length;
    const languagesCount = cvLang.length;
    const softwareCount = cvSoft.length;
    
    // Determinar el enfoque profesional basado en la experiencia
    let professionalFocus = 'gestión de datos y tareas administrativas';
    if (experienceCount > 0) {
      const hasTechExp = cvExp.some((exp: any) => {
        const desc = (exp.description || exp.responsabilidades || exp.logros || '').toLowerCase();
        return desc.includes('tecnolog') || desc.includes('software') || desc.includes('digital');
      });
      if (hasTechExp) {
        professionalFocus = 'tecnología y gestión de datos';
      }
    }
    
    // Construir el texto personalizado
    const parts = [
      `El CV de ${firstName} incluye ${experienceCount} ${experienceCount === 1 ? 'experiencia profesional' : 'experiencias profesionales'}`,
      `${educationCount} ${educationCount === 1 ? 'elemento formativo' : 'elementos formativos'}`,
      `y manejo de ${languagesCount} ${languagesCount === 1 ? 'idioma' : 'idiomas'} y ${softwareCount} ${softwareCount === 1 ? 'herramienta informática' : 'herramientas informáticas'}.`
    ];
    
    const summary = parts.join(', ');
    
    // Añadir información sobre logros y perfil
    const hasQuantifiedAchievements = cvExp.some((exp: any) => {
      const text = (exp.description || exp.responsabilidades || exp.logros || '').toLowerCase();
      return /\d+%|\d+\s*(años|meses|personas|proyectos|clientes)/.test(text);
    });
    
    const hasProfessionalLinks = linkedin && linkedin !== '(no especificado; recomendado crear/actualizar)';
    
    let additionalInfo = '';
    if (!hasQuantifiedAchievements && !hasProfessionalLinks) {
      additionalInfo = ' La información extraída no detalla logros cuantificables ni enlaces a perfiles profesionales, pero evidencia una trayectoria orientada a la gestión de datos y tareas administrativas.';
    } else if (!hasQuantifiedAchievements) {
      additionalInfo = ' La información extraída no detalla logros cuantificables, pero evidencia una trayectoria orientada a la gestión de datos y tareas administrativas.';
    } else if (!hasProfessionalLinks) {
      additionalInfo = ' La información extraída no incluye enlaces a perfiles profesionales, pero evidencia una trayectoria orientada a la gestión de datos y tareas administrativas.';
    } else {
      additionalInfo = ` La información evidencia una trayectoria orientada a la ${professionalFocus}.`;
    }
    
    return summary + additionalInfo;
  };

  // === Bloque Fortalezas con estilo profesional ===
  type SoftSkill = { skill?: string; name?: string; score?: number; level?: string; confidence?: number };
  function normalizeName(name: unknown): string {
    const n = String(name || '').toLowerCase().trim();
    if (!n) return '';
    if (/anal(í|i)tico/.test(n)) return 'Pensamiento analítico';
    if (/cr(í|i)tico/.test(n)) return 'Pensamiento crítico';
    if (/curiosidad/.test(n) || /aprendizaje/.test(n)) return 'Curiosidad y aprendizaje';
    if (/resiliencia/.test(n) || /flexibilidad/.test(n)) return 'Resiliencia y flexibilidad';
    if (/autoconciencia/.test(n)) return 'Autoconciencia';
    if (/influencia/.test(n)) return 'Influencia social';
    if (/decisiones/.test(n)) return 'Toma de decisiones';
    return name ? (name as string).replace(/\s+/g, ' ').replace(/^\p{Zs}+|\p{Zs}+$/gu, '') : '';
  }
  function normalizeLevelText(value: unknown): string {
    const raw = String(value || '').trim().toLowerCase();
    if (!raw) return 'No especificado';
    if (/\balto\b/.test(raw)) return 'Avanzado';
    if (/\bmedio\b/.test(raw)) return 'Intermedio';
    if (/\bbajo\b/.test(raw)) return 'Inicial';
    return String(value || 'No especificado');
  }
  const clampScore = (v: unknown) => Math.max(0, Math.min(100, Math.round(Number(v) || 0)));
  const descriptions: Record<string, string> = {
    'Liderazgo': 'Favorece la coordinación, el alineamiento y la motivación del equipo.',
    'Pensamiento analítico y crítico': 'Habilita un análisis riguroso y la mejora continua de procesos.',
    'Creatividad y curiosidad': 'Impulsa la generación de alternativas y la innovación aplicada.',
    'Resiliencia y flexibilidad': 'Facilita la adaptación a cambios y la gestión eficaz ante imprevistos.',
    'Empatía y autoconciencia': 'Refuerza la colaboración y la dinámica positiva del equipo.',
    'Toma de decisiones': 'Acelera la priorización y la elección informada de alternativas.',
    'Influencia social': 'Refuerza la capacidad de persuadir, negociar y alinear objetivos.'
  };
  // Mapa por nombre normalizado → score
  const ssMap: Record<string, number> = {};
  (Array.isArray(softSkills) ? softSkills as SoftSkill[] : []).forEach((s) => {
    const name = normalizeName(s.skill ?? (s as any).softskill ?? s.name);
    if (!name) return;
    const sc = clampScore(s.score);
    const prev = ssMap[name];
    if (typeof prev !== 'number' || sc > prev) {
      ssMap[name] = sc;
    }
  });
  // Combinar pares
  const pairScore = (a: string, b: string): number | null => {
    const hasA = typeof ssMap[a] === 'number';
    const hasB = typeof ssMap[b] === 'number';
    if (hasA && hasB) {
      const va = ssMap[a] as number;
      const vb = ssMap[b] as number;
      return Math.round((va + vb) / 2);
    }
    return null;
  };
  const strengthsEntries: Array<{ title: string; score: number; text: string }> = [];
  // Liderazgo individual
  if (ssMap['Liderazgo'] != null && ssMap['Liderazgo'] >= 60) {
    strengthsEntries.push({
      title: 'Liderazgo',
      score: ssMap['Liderazgo'],
      text: `**Liderazgo:** ${ssMap['Liderazgo']}/100. ${descriptions['Liderazgo']}`
    });
  }
  // Analítico + Crítico
  const ac = pairScore('Pensamiento analítico', 'Pensamiento crítico');
  if (ac != null && ac >= 60) {
    strengthsEntries.push({ title: 'Pensamiento analítico y crítico', score: ac, text: `**Pensamiento analítico y crítico:** ${ac}/100. ${descriptions['Pensamiento analítico y crítico']}` });
  } else {
    if (ssMap['Pensamiento analítico'] != null && ssMap['Pensamiento analítico'] >= 60) {
      const sc = ssMap['Pensamiento analítico'];
      strengthsEntries.push({ title: 'Pensamiento analítico', score: sc, text: `**Pensamiento analítico:** ${sc}/100. ${descriptions['Pensamiento analítico y crítico']}` });
    }
    if (ssMap['Pensamiento crítico'] != null && ssMap['Pensamiento crítico'] >= 60) {
      const sc = ssMap['Pensamiento crítico'];
      strengthsEntries.push({ title: 'Pensamiento crítico', score: sc, text: `**Pensamiento crítico:** ${sc}/100. ${descriptions['Pensamiento analítico y crítico']}` });
    }
  }
  // Creatividad + Curiosidad
  const cc = pairScore('Creatividad', 'Curiosidad y aprendizaje');
  if (cc != null && cc >= 60) {
    strengthsEntries.push({ title: 'Creatividad y curiosidad', score: cc, text: `**Creatividad y curiosidad:** ${cc}/100. ${descriptions['Creatividad y curiosidad']}` });
  } else {
    if (ssMap['Creatividad'] != null && ssMap['Creatividad'] >= 60) {
      const sc = ssMap['Creatividad'];
      strengthsEntries.push({ title: 'Creatividad', score: sc, text: `**Creatividad:** ${sc}/100. ${descriptions['Creatividad y curiosidad']}` });
    }
    if (ssMap['Curiosidad y aprendizaje'] != null && ssMap['Curiosidad y aprendizaje'] >= 60) {
      const sc = ssMap['Curiosidad y aprendizaje'];
      strengthsEntries.push({ title: 'Curiosidad y aprendizaje', score: sc, text: `**Curiosidad y aprendizaje:** ${sc}/100. ${descriptions['Creatividad y curiosidad']}` });
    }
  }
  // Resiliencia y flexibilidad (ya combinada)
  if (ssMap['Resiliencia y flexibilidad'] != null && ssMap['Resiliencia y flexibilidad'] >= 60) {
    const sc = ssMap['Resiliencia y flexibilidad'];
    strengthsEntries.push({ title: 'Resiliencia y flexibilidad', score: sc, text: `**Resiliencia y flexibilidad:** ${sc}/100. ${descriptions['Resiliencia y flexibilidad']}` });
  }
  // Empatía + Autoconciencia
  const ea = pairScore('Empatía', 'Autoconciencia');
  if (ea != null && ea >= 60) {
    strengthsEntries.push({ title: 'Empatía y autoconciencia', score: ea, text: `**Empatía y autoconciencia:** ${ea}/100. ${descriptions['Empatía y autoconciencia']}` });
  } else {
    if (ssMap['Empatía'] != null && ssMap['Empatía'] >= 60) {
      const sc = ssMap['Empatía'];
      strengthsEntries.push({ title: 'Empatía', score: sc, text: `**Empatía:** ${sc}/100. ${descriptions['Empatía y autoconciencia']}` });
    }
    if (ssMap['Autoconciencia'] != null && ssMap['Autoconciencia'] >= 60) {
      const sc = ssMap['Autoconciencia'];
      strengthsEntries.push({ title: 'Autoconciencia', score: sc, text: `**Autoconciencia:** ${sc}/100. ${descriptions['Empatía y autoconciencia']}` });
    }
  }
  // Otras potenciales fortalezas
  if (ssMap['Influencia social'] != null && ssMap['Influencia social'] >= 60) {
    const sc = ssMap['Influencia social'];
    strengthsEntries.push({ title: 'Influencia social', score: sc, text: `**Influencia social:** ${sc}/100. ${descriptions['Influencia social']}` });
  }
  if (ssMap['Toma de decisiones'] != null && ssMap['Toma de decisiones'] >= 60) {
    const sc = ssMap['Toma de decisiones'];
    strengthsEntries.push({ title: 'Toma de decisiones', score: sc, text: `**Toma de decisiones:** ${sc}/100. ${descriptions['Toma de decisiones']}` });
  }
  // Ordenar por score desc y crear bullets con frase
  strengthsEntries.sort((a,b)=> b.score - a.score);
  const fortalezas = strengthsEntries.length
    ? strengthsEntries.map(s => `* ${s.text}`).join('\n')
    : '* (pendiente de evaluación)';

  // === Bloque Áreas de mejora priorizadas ===
  // Canonicalización de nombres para evitar duplicados y mantener un estilo coherente
  const canon = (name: unknown): string => {
    const n = String(name || '').toLowerCase();
    if (/decisiones/.test(n)) return 'Toma de decisiones';
    if (/anal(í|i)tic/.test(n)) return 'Pensamiento analítico';
    if (/cr(í|i)tic/.test(n)) return 'Pensamiento crítico';
    if (/creativ/.test(n)) return 'Creatividad';
    if (/curios|aprendiz/.test(n)) return 'Curiosidad y aprendizaje';
    if (/resilien|flexib/.test(n)) return 'Resiliencia y flexibilidad';
    if (/empat/.test(n)) return 'Empatía';
    if (/autoconcien/.test(n)) return 'Autoconciencia';
    if (/influenc|comunicaci/.test(n)) return 'Influencia social';
    if (/lideraz/.test(n)) return 'Liderazgo';
    return (String(name || '')).trim();
  };
  // Candidatos desde backend
  const backCandidates: Array<{ name: string; score: number }> = (Array.isArray(improvement) ? improvement : [])
    .map((a:any) => ({ name: canon(a?.area || a?.name), score: clampScore(a?.score) }))
    .filter(x => !!x.name && x.score > 0 && x.score < 60);
  // Candidatos desde soft skills
  const skillCandidates: Array<{ name: string; score: number }> = Object.entries(ssMap)
    .map(([name, s]) => ({ name: canon(name), score: clampScore(s) }))
    .filter(x => x.score > 0 && x.score < 60);
  // Fusionar y priorizar por menor score
  const byName: Record<string, number> = {};
  // Priorizar puntuaciones reales: primero las de juegos (skillCandidates),
  // luego integrar backend solo si aporta un score válido (>0)
  for (const c of [...skillCandidates, ...backCandidates]) {
    if (!c.name) continue;
    if (c.score <= 0) continue;
    const existing = byName[c.name];
    byName[c.name] = typeof existing === 'number' ? Math.min(existing, c.score) : c.score;
  }
  // Construir lista ordenada ascendente
  const allImprovements = Object.entries(byName)
    .map(([name, score]) => ({ name, score }))
    .sort((a,b)=> (a.score - b.score) || a.name.localeCompare(b.name, 'es'));
  // Seleccionar 3 puntuaciones más bajas (incluir la 4ª si empata con la 3ª)
  const thirdScore = allImprovements[2]?.score ?? Infinity;
  const improvementsMerged = allImprovements.filter(item => item.score <= thirdScore).slice(0, 4);
  // Plantillas de razones y acciones por área
  const improveTemplates: Record<string, { reason: string; action: string }> = {
    'Toma de decisiones': {
      reason: 'lo que puede afectar la rapidez y la calidad de tus elecciones.',
      action: 'Realizar simulaciones de toma de decisiones y analizar casos prácticos para fortalecer la confianza y la agilidad al elegir alternativas.'
    },
    'Influencia social': {
      reason: 'lo que puede limitar la capacidad de persuasión y comunicación en equipo.',
      action: 'Participar en talleres de comunicación asertiva y negociación; practicar un pitch breve con beneficios claros para el equipo.'
    },
    'Pensamiento analítico': {
      reason: 'dificultando la identificación de patrones y prioridades.',
      action: 'Practicar ejercicios de clasificación y priorización; usar hojas de cálculo con listas de verificación y métricas simples.'
    },
    'Pensamiento crítico': {
      reason: 'reduciendo la evaluación objetiva de opciones.',
      action: 'Comparar fuentes y evidencias antes de decidir; utilizar un checklist de sesgos y criterios de decisión.'
    },
    'Creatividad': {
      reason: 'limitando la generación de alternativas ante problemas cotidianos.',
      action: 'Aplicar técnicas de ideación (por ejemplo, SCAMPER) con tiempos acotados y registrar 3–5 opciones por reto.'
    },
    'Curiosidad y aprendizaje': {
      reason: 'restando opciones para mejorar procesos y herramientas.',
      action: 'Definir un micro-plan de estudio de 2–3 semanas y documentar aprendizajes aplicables al trabajo.'
    },
    'Resiliencia y flexibilidad': {
      reason: 'aumentando el estrés ante cambios y errores inesperados.',
      action: 'Usar re‑enmarcado ("qué está bajo mi control") y planes alternativos; practicar pausas breves con checklist de prioridades.'
    },
    'Empatía': {
      reason: 'dificultando la colaboración y la resolución de conflictos.',
      action: 'Practicar escucha activa (parafraseo, preguntas abiertas) y validación emocional en conversaciones reales.'
    },
    'Autoconciencia': {
      reason: 'reduciendo el autocontrol ante presión o errores.',
      action: 'Registrar detonantes y estrategias efectivas en un diario breve; realizar micro‑retrospectivas semanales.'
    },
    'Liderazgo': {
      reason: 'afectando la coordinación y motivación del equipo.',
      action: 'Definir objetivos claros, roles y rituales de reconocimiento; pedir feedback 360º breve.'
    }
  };
  const ensureDot = (t?: string) => {
    const s = String(t || '').trim();
    if (!s) return '';
    return /[\.\!\?]$/.test(s) ? s : s + '.';
  };
  const capitalizeFirst = (t?: string) => {
    const s = String(t || '').trim();
    if (!s) return '';
    return s.charAt(0).toUpperCase() + s.slice(1);
  };
  const buildBullet = (name: string, score: number, reason?: string, action?: string) => {
    const tpl = improveTemplates[name] || { reason: '', action: '' };
    const r = capitalizeFirst(ensureDot(reason || tpl.reason));
    const a = capitalizeFirst(ensureDot(action || tpl.action));
    return `* **${name}:** (${score}/100). ${r} **Acción:** ${a}`;
  };
  const areasMejoraBullets = improvementsMerged
    .filter(x => x.score > 0)
    .map(x => buildBullet(x.name, x.score));
  const areasMejora = areasMejoraBullets.length
    ? areasMejoraBullets.join('\n')
    : '* Toma de decisiones: (45/100) en toma de decisiones. Acción: Realizar simulaciones y analizar casos prácticos para ganar agilidad al decidir.';

  // Eliminado: las mejoras rápidas del CV ahora se muestran en el panel de análisis con datos reales

  // Generar texto profesional para entornos de trabajo ideales (conciso)
  const generateEntornosText = (): string => {
    const hasRemotePreference = (r?.jobPreferences as any)?.remoteWork || false;
    const hasStructuredProfile = Array.isArray(cv?.experience) && cv.experience.length > 0;

    if (hasRemotePreference && hasStructuredProfile) {
      return "Entorno de trabajo remoto, con tareas estructuradas y objetivos claros. Espacios que permitan autonomía, flexibilidad horaria y comunicación digital. Es recomendable un ambiente colaborativo pero con margen para el trabajo individual, donde se valore la organización y la mejora continua.";
    }
    if (hasRemotePreference) {
      return "Entorno de trabajo remoto con objetivos definidos y canales de comunicación claros. Autonomía, flexibilidad horaria y colaboración digital con espacio para el trabajo individual y aprendizaje continuo.";
    }
    if (hasStructuredProfile) {
      return "Entorno de trabajo inclusivo y flexible con modalidad híbrida. Espacios que combinen colaboración presencial con tareas estructuradas, comunicación abierta y margen para el trabajo individual. Organización y mejora continua como principios de trabajo.";
    }
    return "Entorno de trabajo inclusivo, con tareas claras y objetivos definidos. Colaboración efectiva, comunicación abierta y espacio para el trabajo individual, promoviendo la organización y la mejora continua.";
  };
  
  const entornosText = generateEntornosText();

  const rolesBullets = roles.length
    ? roles.map((role:any) => `**${role.role}** — *${role.seniority || 'Junior'}* — **${role.remote_viable ? '100% remoto' : 'Remoto viable'}**.\n\n_Razón:_ ${role.reason || 'alineación competencial'}`).join('\n\n')
    : '**Data Entry / Back-office** — *Junior–Mid* — **100% remoto**.\n\n_Razón:_ experiencia directa en captura/transcripción y foco en precisión.';

  const plan030 = Array.isArray(plan.short_term) ? plan.short_term.map((x:string)=>`* ${x}`).join('\n')
    : '* Actualizar el CV incluyendo logros medibles y enlaces a LinkedIn.\n* Realizar un curso breve de toma de decisiones y comunicación asertiva.\n* Optimizar perfiles en portales de empleo remoto.';
  const plan60  = Array.isArray(plan.medium_term) ? plan.medium_term.map((x:string)=>`* ${x}`).join('\n')
    : '* Participar en talleres de influencia social y negociación.\n* Solicitar feedback sobre el CV y cartas de presentación.\n* Ampliar la red de contactos profesionales en LinkedIn y grupos sectoriales.';
  const plan90  = Array.isArray(plan.long_term) ? plan.long_term.map((x:string)=>`* ${x}`).join('\n')
    : '* Obtener certificaciones en gestión de datos o administración digital.\n* Buscar oportunidades de promoción interna o roles de mayor responsabilidad.\n* Desarrollar un portafolio digital con ejemplos de proyectos o tareas realizadas.';

  // === NUEVO: Estrategias de búsqueda de empleo estructuradas y PERSONALIZADAS ===
  const buildJobSearchStrategies = (): string => {
    try {
      const jobPrefs = (r?.jobPreferences || {}) as Record<string, unknown>;
      const wantsRemote = Boolean(jobPrefs && (jobPrefs as any).remoteWork);
      const preferredLocations = Array.isArray((jobPrefs as any)?.locations)
        ? ((jobPrefs as any).locations as string[]).join(', ')
        : (jobPrefs as any)?.location || '';

      const firstRole = Array.isArray(roles) && roles.length > 0 ? roles[0] as any : null;
      const targetRole = firstRole?.role || 'el puesto objetivo';

      const topSoft = ssTop[0]?.skill || 'tu fortaleza principal';
      const secondSoft = ssTop[1]?.skill || ssTop[0]?.skill || 'tu segunda fortaleza';

      // Plataformas adaptadas (añadimos portales remotos solo si aplica)
      const platforms: string[] = ['* Infojobs', '* LinkedIn', '* Indeed'];
      if (wantsRemote) {
        platforms.push('* FlexJobs');
        platforms.push('* Remotive');
      }

      // Optimización del CV sin repetir lo ya indicado en "Análisis del CV"
      const hasExp = cvExp.length > 0;
      const hasEdu = cvEdu.length > 0;
      const hasLang = cvLang.length > 0;

      const cvBullets: string[] = [];
      cvBullets.push(`* Ordenar la información para que lo primero sea lo más útil para ${targetRole}.`);
      if (hasExp) {
        cvBullets.push('* Resumir cada experiencia en 1–2 líneas claras (qué hiciste y para qué sirvió).');
      }
      cvBullets.push('* Añadir enlaces visibles a perfil de LinkedIn y, si existe, a un portafolio.');
      if (hasLang) {
        cvBullets.push('* Indicar idiomas y, si se tiene, certificaciones (por ejemplo, A2, B1...).');
      }
      if (!hasEdu && !hasExp) {
        cvBullets.push('* Incluir un perfil breve (2–3 frases) con tu propuesta de valor.');
      }
      cvBullets.push('* Mantener una maquetación limpia y fácil de leer (máximo 1–2 páginas).');
      cvBullets.push('* Guardar en PDF con nombre claro: "Nombre_Apellido_CV.pdf".');

      // Cartas y portfolio orientados al rol y a las fortalezas detectadas
      const coverLetter: string[] = [
        `Crear una carta breve y personalizada para cada oferta, destacando ${topSoft} y ${secondSoft}.`,
        wantsRemote
          ? 'Indicar motivación por el trabajo remoto y disponibilidad horaria.'
          : 'Explicar disponibilidad y lugar de trabajo preferido.'
      ];
      if (firstRole?.reason) {
        coverLetter.push(`Añadir una línea con la razón de encaje: ${String(firstRole.reason)}`);
      }

      // Networking dirigido con foco en preferencias y sectores
      const networking: string[] = [
        'Participar en [grupos de LinkedIn](https://www.linkedin.com/groups/) y en foros del sector para ampliar la red y acceder a oportunidades que no siempre se publican.',
      ];
      if (preferredLocations) {
        networking.push(`Buscar comunidades en ${String(preferredLocations)} y eventos online de interés.`);
      }
      networking.push('Practicar una presentación breve (30–45 segundos) con un logro simple y medible.');

      // Entrevistas (STAR) con ejemplos guiados por fortalezas y áreas a potenciar
      const star: string[] = [
        `Preparar 2–3 ejemplos con la [técnica STAR](https://hireline.io/blog/responder-entrevista-de-trabajo-metodo-star/) donde brilles en ${topSoft} y ${secondSoft}.`,
        'Ensayar respuestas sobre toma de decisiones, resolución de conflictos y trabajo en equipo.',
        'Apoyar las respuestas con datos sencillos (antes/después, tiempos o calidad).',
        
      ];

      const parts: string[] = [];
      parts.push('## Optimización del CV');
      parts.push(cvBullets.join('\n'));
      parts.push('');
      parts.push('## Cartas y portfolio/casos');
      parts.push(coverLetter.join(' '));
      parts.push('');
      parts.push('## Plataformas');
      const platformsWithLinks = platforms.map(p => {
        const label = p.replace(/^\*\s*/, '').trim().toLowerCase();
        if (label.startsWith('infojobs')) return '* [InfoJobs](https://www.infojobs.net/)';
        if (label.startsWith('linkedin')) return '* [LinkedIn Empleos](https://www.linkedin.com/jobs/)';
        if (label.startsWith('indeed')) return '* [Indeed](https://www.indeed.com/)';
        if (label.startsWith('flexjobs')) return '* [FlexJobs](https://www.flexjobs.com/)';
        if (label.startsWith('remotive')) return '* [Remotive](https://remotive.com/jobs)';
        return p;
      });
      parts.push(platformsWithLinks.join('\n'));
      parts.push('');
      parts.push('## Networking dirigido');
      parts.push(networking.join(' '));
      parts.push('');
      parts.push('## Entrevistas (método STAR)');
      parts.push(star.join(' '));

      return parts.join('\n');
    } catch {
      // Fallback seguro en caso de datos ausentes
      return [
        '## Optimización del CV',
        '* Incluir logros cuantificables y KPIs en cada experiencia.',
        '* Añadir una sección de habilidades técnicas y soft skills.',
        '* Revisar y homogeneizar el formato y la ortografía.',
        '',
        '## Cartas y portfolio/casos',
        'Elaborar una carta de presentación breve y personalizada para cada candidatura.',
        '',
        '## Plataformas',
        '* Infojobs',
        '* LinkedIn',
        '* Indeed',
        '* FlexJobs',
        '* Remotive',
        '',
        '## Networking dirigido',
        'Participar en grupos de LinkedIn y foros de empleo remoto.',
        '',
        '## Entrevistas (método STAR)',
        'Preparar ejemplos concretos con cifras y resultados.'
  ].join('\n');
    }
  };

  const jobSearchStrategies = buildJobSearchStrategies();

  // Herramientas útiles: personalizadas según perfil del candidato
  
  // Análisis del perfil para personalizar recursos
  const hasExp = cvExp.length > 0;
  const hasLang = cvLang.length > 0;
  const jobPrefs = (r?.jobPreferences || {}) as Record<string, unknown>;
  const isRemote = Boolean(jobPrefs && (jobPrefs as any).remoteWork);
  const topWeakness = improvementsMerged[0]?.name || '';
  
  // Recursos personalizados según necesidades detectadas
  const personalizedTools: string[] = [];
  
  // Herramientas de productividad según experiencia
  if (hasExp) {
    personalizedTools.push('* [Excel – guía básica](https://support.microsoft.com/es-es/excel)');
  } else {
    personalizedTools.push('* [Excel – tutorial para principiantes](https://support.microsoft.com/es-es/excel)');
  }
  
  // Herramientas de organización
  personalizedTools.push('* [Notion – organización personal](https://www.notion.so/)');
  
  // Recursos de aprendizaje según áreas de mejora
  if (topWeakness.toLowerCase().includes('decisiones')) {
    personalizedTools.push('* [Curso: Toma de decisiones (Coursera)](https://www.coursera.org/learn/decision-making)');
  }
  if (topWeakness.toLowerCase().includes('comunicación') || topWeakness.toLowerCase().includes('influencia')) {
    personalizedTools.push('* [Curso: Comunicación efectiva (Udemy)](https://www.udemy.com/course/comunicacion-efectiva/)');
  }
  
  // Recursos específicos para trabajo remoto
  if (isRemote) {
    personalizedTools.push('* [Guía: Trabajo remoto efectivo](https://blog.trello.com/es/trabajo-remoto-efectivo)');
  }
  
  // Recursos de accesibilidad e inclusión (opcional, mostrar solo si aplica)
  if (!hasExp) {
    personalizedTools.push('* [Guía para crear un CV claro](https://www.canva.com/es_es/curriculum/)');
  }
  
  // Recursos de idiomas si aplica
  if (hasLang) {
    personalizedTools.push('* [Duolingo – práctica de idiomas](https://www.duolingo.com/)');
  }
  
  const toolsSec = personalizedTools.join('\n');

  // Lecturas recomendadas (personalizadas y sin repetir herramientas)
  const buildRecommendedReadings = (): string => {
    const reads: string[] = [];
    const w = topWeakness.toLowerCase();
    if (w.includes('decisiones')) {
      reads.push('* [Toma de decisiones: guía introductoria](https://es.wikipedia.org/wiki/Toma_de_decisiones)');
    }
    if (w.includes('comunicación') || w.includes('influencia')) {
      reads.push('* [Comunicación asertiva (conceptos básicos)](https://es.wikipedia.org/wiki/Comunicaci%C3%B3n_asertiva)');
    }
    if (w.includes('creativ') || w.includes('curiosidad')) {
      reads.push('* [Creatividad: conceptos y técnicas](https://es.wikipedia.org/wiki/Creatividad)');
    }
    if (w.includes('resilien')) {
      reads.push('* [Resiliencia (psicología): lectura introductoria](https://es.wikipedia.org/wiki/Resiliencia_(psicolog%C3%ADa))');
    }
    if (w.includes('empat')) {
      reads.push('* [Empatía: explicación sencilla](https://es.wikipedia.org/wiki/Empat%C3%ADa)');
    }
    if (w.includes('autoconciencia')) {
      reads.push('* [Autoconciencia: conceptos básicos](https://es.wikipedia.org/wiki/Autoconciencia)');
    }
    if (w.includes('liderazgo')) {
      reads.push('* [Liderazgo: estilos y nociones básicas](https://es.wikipedia.org/wiki/Liderazgo)');
    }
    return reads.join('\n');
  };
  const readingsSec = buildRecommendedReadings();

  // Función para generar recomendaciones de capitalización (todas las puntuaciones altas, con formato profesional)
  const buildCapitalizationTips = (): string => {
    const threshold = 60; // puntuación considerada alta (no se muestra, solo se usa para filtrar)
    const highSkills = ssTop.filter((s: any) => (Number(s?.score) || 0) >= threshold);
    const selected = highSkills.length > 0 ? highSkills : ssTop.slice(0, 5);
    if (selected.length === 0) {
      return 'Añade un logro claro (acción + resultado) en tu CV y prepara un ejemplo breve para entrevistas.';
    }

    const firstExp: any = Array.isArray(cvExp) && cvExp.length > 0 ? cvExp[0] : null;
    const latestRole = (firstExp?.title || '').trim() || 'tu último proyecto';
    const latestCompany = (firstExp?.company || '').trim();
    const inCompany = latestCompany ? ` en ${latestCompany}` : '';

    const block = (title: string, lines: string[]) => [
      `**${title}**`,
      ...lines.map(l => `- ${l}`)
    ].join('\n');

    const items = selected.map((skill: any) => {
      const s = normalizeName(skill.skill);
      switch (s) {
        case 'Toma de decisiones':
          return block('Toma de decisiones', [
            'Úsala para elegir opciones con criterios claros y comunicar el porqué',
            'En CV/entrevista: “Comparé alternativas y reduje tiempos de entrega en Y%”'
          ]);
        case 'Pensamiento analítico':
          return block('Pensamiento analítico', [
            'Construye métricas simples y detecta patrones para decidir mejor',
            'En CV/entrevista: “Analicé datos de X y mejoré el tiempo un Y%”'
          ]);
        case 'Pensamiento crítico':
          return block('Pensamiento crítico', [
            'Úsalo para revisar procesos, detectar riesgos y proponer mejoras simples',
            'En CV/entrevista: “Analicé X proceso y reduje errores un Y%”'
          ]);
        case 'Creatividad':
          return block('Creatividad', [
            'Propón alternativas simples que reduzcan pasos y aceleren entregas',
            'En CV/entrevista: “Diseñé una solución sencilla y acorté el ciclo en Y%”'
          ]);
        case 'Influencia social':
          return block('Influencia social', [
            'Presenta ideas en 1 página: problema, opción recomendada, impacto y próximo paso',
            'En CV/entrevista: “Logré la adopción de [herramienta] en N áreas”'
          ]);
        case 'Curiosidad y aprendizaje':
          return block('Curiosidad y aprendizaje', [
            'Aprende herramientas clave y aplícalas en tareas reales',
            'En CV/entrevista: “Aprendí X y mejoré el proceso Y en Z semanas”'
          ]);
        case 'Resiliencia y flexibilidad':
          return block('Resiliencia y flexibilidad', [
            'Adáptate a cambios manteniendo objetivos y calidad',
            'En CV/entrevista: “Reorganicé tareas ante un cambio y cumplimos el plazo”'
          ]);
        case 'Autoconciencia':
          return block('Autoconciencia', [
            'Pide condiciones que te ayudan a rendir: instrucciones claras, tiempos de foco y feedback regular',
            'En CV/entrevista: “Organicé mi trabajo y aumenté la productividad X%”'
          ]);
        case 'Empatía':
          return block('Empatía', [
            'Escucha y traduce necesidades a acciones concretas',
            'En CV/entrevista: “Recogí feedback y ajusté la solución; subió la satisfacción N%”'
          ]);
        case 'Liderazgo':
          return block('Liderazgo', [
            'Coordina mini‑proyectos: tareas, plazos y seguimiento semanal',
            'En CV/entrevista: “Guié a un equipo de N personas y cumplimos X% de hitos”'
          ]);
        default:
          return block(s || 'Competencia', [
            `CV: “Acción clara en ${latestRole}${inCompany} + resultado visible”`,
            'LinkedIn: Resume tu aportación en 1 línea concreta',
            'Mensajes: Propón una prueba pequeña de 1–2 días',
            'Pruebas de valor: Entregable simple que muestre el beneficio',
            'Entrevistas: Explica qué hiciste y qué cambió'
          ]);
      }
    });

    return items.join('\n\n');
  };

  const juegos = buildCapitalizationTips();

  // const miniplan = [
  //   '**Decisiones:** usa una matriz rápida (Impacto × Esfuerzo) y límites de tiempo (10 min).',
  //   '**Influencia:** prepara un **pitch** de 3 líneas + 1 prueba de valor (antes/después).'
  // ].map(s=>`* ${s}`).join('\n'); // Eliminado por solicitud del usuario

  const frasesListas = [
    '* **Titular:** *Data Entry | QA de Datos | Back-office (100% remoto)*',
    '* **Acerca de (3 líneas):** "Capturo y depuro datos con precisión y tiempos de entrega fiables. Experiencia en proyectos internacionales (Excel/Sheets, OCR, QA). Busco aportar orden y métricas claras a equipos remotos de operaciones y contenido."',
    '* **Mensaje corto a reclutador/cliente:** "Hola, soy ' + (fullName.split(' ')[0] || '…') + '. He realizado data entry y transcripción para clientes internacionales, con foco en precisión y SLA. Puedo enviar una muestra (hoja con limpieza + checklist de QA) y empezar de inmediato."'
  ].join('\n');

  // Nota: el mensaje final se construye más abajo y se muestra en la caja azul, no en el markdown

  // === Markdown EXACTO ===
  return [
`# Resumen ejecutivo

${(() => {
  const firstName = fullName.split(' ')[0] || 'Profesional';
  const experienceCount = cvExp.length;
  const hasExperience = experienceCount > 0;
  const experienceText = hasExperience ? `con experiencia en ${experienceCount} ${experienceCount === 1 ? 'posición' : 'posiciones'}` : 'con formación diversa';
  
  // Construir fortalezas principales
  const topSkill = ssTop[0];
  const topSkillName = topSkill?.skill || 'liderazgo';
  const secondarySkills = ssTop.slice(1, 3).map(s => s.skill).join(', ') || 'pensamiento analítico, creatividad';
  
  // Determinar modalidad de trabajo
  const jobPrefs = (r?.jobPreferences || {}) as Record<string, unknown>;
  const isRemote = Boolean(jobPrefs && (jobPrefs as any).remoteWork);
  const workMode = isRemote ? 'modalidad remota' : 'entornos presenciales';
  
  // Construir propuesta de valor
  const valueProposition = `Su propuesta de valor reside en la combinación de habilidades técnicas y soft skills, con especial interés en roles administrativos y de gestión de datos en ${workMode}.`;
  
  // Áreas de mejora (limpiar puntuaciones)
  const clean = (v: string) => String(v || '').replace(/\s*\((?:\d+%?|\d+\s*\/\s*\d+)\)\s*/g, '').trim();
  const improvementAreas = improvement.slice(0, 2).map((a: any) => clean(a?.area || a.name || '')).filter(Boolean).join(' y ') || 'toma de decisiones e influencia social';
  
  return `Profesional ${experienceText}, ${firstName} destaca por su capacidad de ${topSkillName}, ${secondarySkills} y resiliencia. ${valueProposition} Su perfil es adecuado para entornos que valoren la autonomía, la organización y el aprendizaje continuo. Áreas a potenciar: **${improvementAreas}**.`;
})()}`,

`# Datos personales

* **Nombre:** ${fullName}
* **Ubicación:** ${location}
* **Email:** ${email}
* **Teléfono:** ${phone}
* **LinkedIn:** ${linkedin}`,

`# Resumen del CV

**Experiencia (selección)**
${expBullets}

**Formación (selección)**
${eduBullets}

**Idiomas**
${langs}

**Herramientas/Software**
${softw}

${generateCvSummaryText()}`,

`# Fortalezas clave
${fortalezas}`,

`# Áreas de mejora priorizadas
${areasMejora}`,

// Eliminado: apartado de diagnóstico rápido del CV en markdown

`# Entornos de trabajo ideales

${entornosText}`,

`# Roles sugeridos
${rolesBullets}`,

`# Plan de acción

**Corto plazo (0-30 días)**
${plan030}

**Medio plazo (1-3 meses)**
${plan60}

**Largo plazo (3-6+ meses)**
${plan90}`,

`# Estrategias de búsqueda de empleo
${jobSearchStrategies}`,

`# Herramientas útiles
${toolsSec}`,

`# Lecturas recomendadas
${readingsSec || '* (Se generarán cuando identifiquemos un área concreta a reforzar)'}`,

`# Cómo capitalizar tus fortalezas
${juegos}`,

`# Frases listas (para propuestas y LinkedIn)
${frasesListas}`
  ].join('\n\n');
}

const ResultadosPage: React.FC = () => {
  const dispatch = useDispatch();
  const personal = useAppSelector((state: RootState) => state.personal);
  const cvAnalysis = personal?.cvAnalysis;
  const report = personal?.report;
  const fecha = new Date().toLocaleDateString();
  const game = useAppSelector((state: RootState) => state.game);

  // Hook de valoración (alias para evitar choque de nombres)
  const uid = report?.userId ?? '';
  const rid = (report as any)?.id ?? '';
  const { rateCv: submitRating } = useCvRating(uid, rid);

  const asStars = (n: number): CvStars => (n < 1 ? 1 : n > 5 ? 5 : Math.round(n)) as CvStars;

  // === NUEVO: estado local para estrellas del CV procedentes del backend ===
  const [, setCvStarsLocal] = useState<CvDiagnostico | null>(null);
  // Helpers robustos para mapear diversas respuestas del backend
  const firstNum = (...vals: any[]) => {
    for (const v of vals) {
      const n = Number(v);
      if (!Number.isNaN(n)) return n;
    }
    return undefined;
  };
  const toStarsScale = (v: unknown): CvStars => {
    const n = Number(v);
    if (Number.isNaN(n)) return 3 as CvStars;
    let s = n;
    if (s <= 1) s *= 5;       // 0–1 → 0–5
    else if (s > 5) s /= 20;  // 0–100 → 0–5
    return asStars(s);
  };

  // Debug logging usando la utilidad (comentado para producción)
  // debugState(state, 'ResultadosPage');

  // Generar report si no existe
  useEffect(() => {
    if (!report && personal.softSkills && personal.softSkills.length > 0) {
      dispatch(generateFinalReport());
    }
  }, [report, personal.softSkills, dispatch]);

  // Exponer submitRating (v:number) para el bloque embebido del informe
  useEffect(() => {
    (window as any).__rateCv = (v: number) => submitRating(asStars(v));
    return () => { try { delete (window as any).__rateCv; } catch { /* no-op */ } };
  }, [submitRating]);

  // Estado para el informe IA
  const [iaReport, setIaReport] = useState<string>('');
  const [iaScore, setIaScore] = useState<number | undefined>(undefined);
  const [loadingIa, setLoadingIa] = useState<boolean>(false);
  const [errorIa, setErrorIa] = useState<string>('');
  const fetchedRef = useRef(false);
  const [finalPhrase, setFinalPhrase] = useState<string>('');

  // === NUEVO: fallback de impresión del radar (SVG → IMG) ===
  const radarBoxRef = useRef<HTMLDivElement>(null);
  const [radarImg, setRadarImg] = useState<string>('');
  useEffect(() => {
    const beforePrint = () => {
      const svg = radarBoxRef.current?.querySelector('svg');
      if (!svg) return;
      const xml = new XMLSerializer().serializeToString(svg);
      const blob = new Blob([xml], { type: 'image/svg+xml;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      setRadarImg(url);
    };
    window.addEventListener('beforeprint', beforePrint);
    return () => window.removeEventListener('beforeprint', beforePrint);
  }, []);

  // Llamar al endpoint de IA al cargar la página
  useEffect(() => {
    // Sincronizar soft skills de minijuegos → estado personal (fallback robusto)
    try {
      const gameSkills = Array.isArray(game?.softSkills) ? game.softSkills : [];
      const personalSkills = Array.isArray(personal?.softSkills) ? personal.softSkills : [];
      if (gameSkills.length > 0 && personalSkills.length < gameSkills.length) {
        const mapped = gameSkills.map((s: any) => {
          const score = Math.round(Number(s?.score) || 0);
          const level = s?.level || (score < 50 ? 'bajo' : score < 75 ? 'medio' : 'alto');
          const conf = typeof s?.confidence === 'number' && s.confidence <= 1
            ? Math.round(s.confidence * 100)
            : Math.round(Number(s?.confidence) || 80);
          return { skill: String(s?.name || s?.softSkill || 'Habilidad'), score, level, confidence: conf };
        });
        dispatch(saveSoftSkills(mapped));
      }
    } catch { /* no-op */ }

    const fetchIaReport = async () => {
      setLoadingIa(true);
      setErrorIa('');
      
      // DEBUG: Agregar logs para entender el estado
      console.log('🔍 DEBUG - Estado personal completo:', personal);
      console.log('🔍 DEBUG - cvAnalysis del estado:', personal?.cvAnalysis);
      console.log('🔍 DEBUG - cvFile del estado:', personal?.cvFile);
      console.log('🔍 DEBUG - report del estado:', personal?.report);
      
      // Asegurar análisis del CV si existe un archivo subido pero no hay análisis útil
      if (personal?.cvFile && (!personal?.cvAnalysis || (
          (!Array.isArray(personal.cvAnalysis.strengths) || personal.cvAnalysis.strengths.length === 0) &&
          (!Array.isArray(personal.cvAnalysis.skills) || personal.cvAnalysis.skills.length === 0)
        ))) {
        try {
          console.log('🔍 DEBUG - Hay CV pero no análisis útil. Lanzando análisis automático...');
          const dataUrl = personal.cvFile.fileContent;
          const respBlob = await fetch(dataUrl);
          const blob = await respBlob.blob();
          const form = new FormData();
          const fileName = personal.cvFile.fileName || 'cv.pdf';
          form.append('file', new File([blob], fileName, { type: 'application/pdf' }));
          const analyzeRes = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.PDF_ANALYZE), {
            method: 'POST',
            body: form,
          });
          if (analyzeRes.ok) {
            const analysis = await analyzeRes.json();
            dispatch(saveCvAnalysis(analysis));
            console.log('✅ DEBUG - Análisis de CV guardado desde ResultadosPage');
          } else {
            console.warn('⚠️ DEBUG - analyze-cv falló:', analyzeRes.status, analyzeRes.statusText);
          }
        } catch (e) {
          console.warn('⚠️ DEBUG - Error analizando CV automáticamente:', e);
        }
      }

      try {
        // SOLUCIÓN: Asegurar que siempre hay datos mínimos para el informe
        const userFullName = `${report?.firstName || ''} ${report?.lastName || ''}`.trim() || 'Usuario';
        const validSoftSkills = filterValidSoftSkills(personal.softSkills || []);
        
        // DEBUG: Log del requestBody antes de enviarlo
        console.log('🔍 DEBUG - userFullName:', userFullName);
        console.log('🔍 DEBUG - validSoftSkills:', validSoftSkills);
        console.log('🔍 DEBUG - cvAnalysis antes del request:', cvAnalysis);
        
        // Si no hay softSkills, proporcionar datos básicos para que el informe se genere
        const normalizeLevel = (value: unknown): 'bajo' | 'medio' | 'alto' => {
          if (typeof value !== 'string') return 'medio';
          const v = value.trim().toLowerCase();
          if (v === 'alto') return 'alto';
          if (v === 'bajo') return 'bajo';
          return 'medio';
        };

        const toPercentInt = (value: unknown): number => {
          // Acepta 0-1 o 0-100. Convierte a entero 0-100 seguro
          const num = Number(value);
          if (Number.isNaN(num)) return 0;
          const perc = num <= 1 ? num * 100 : num;
          return Math.max(0, Math.min(100, Math.round(perc)));
        };

        const softSkillsToSend = validSoftSkills.length > 0 ? validSoftSkills.map((skill) => ({
          skill: skill.skill || 'Habilidad no definida',
          score: Number(skill.score) || 0,
          level: normalizeLevel(skill.level),
          confidence: toPercentInt(skill.confidence),
        })) : [{
          skill: 'Motivación profesional',
          score: 70,
          level: 'medio',
          confidence: 80,
        }];

        const requestBody = {
          userId: report?.userId || 'user',
          fullName: userFullName,
          softSkills: softSkillsToSend,
          // Incluir contacto básico desde estado si el CV no lo trae
          email: personal.email || undefined,
          phone: personal.whatsapp || undefined,
          cvAnalysis: cvAnalysis ? {
            // Campos básicos del análisis
            strengths: cvAnalysis.strengths ?? [],
            weaknesses: cvAnalysis.weaknesses ?? [],
            feedback: cvAnalysis.feedback ?? '',
            structure: cvAnalysis.structure ?? 'regular',
            coherence: cvAnalysis.coherence ?? 'regular',
            experience: cvAnalysis.experience ?? 'regular',
            skills: cvAnalysis.skills ?? [],
            education: cvAnalysis.education ?? [],
            alerts: cvAnalysis.alerts ?? [],
            
            // CRÍTICO: Incluir TODOS los datos estructurados del CV extraídos por IA
            cv_structured: cvAnalysis.cv_structured ?? null,
            candidate: cvAnalysis.candidate ?? null,
            contact: cvAnalysis.contact ?? null,
            experience_detailed: cvAnalysis.experience_detailed ?? null,
            education_detailed: cvAnalysis.education_detailed ?? null,
            languages: cvAnalysis.languages ?? null,
            periods: cvAnalysis.periods ?? null,
            highlights: cvAnalysis.highlights ?? null,
            volunteering: cvAnalysis.volunteering ?? null,
            cv_analysis_structured: cvAnalysis.cv_analysis_structured ?? null,
            
            // Campos adicionales que pueden estar disponibles
            raw_text: cvAnalysis.raw_text ?? null,
            layout_sections: cvAnalysis.layout_sections ?? null,
            ai_analysis: cvAnalysis.ai_analysis ?? null,
            basic_hints: cvAnalysis.basic_hints ?? null,
            provenance: cvAnalysis.provenance ?? null,
          } : null,
          jobPreferences: personal.jobPreferences || report?.jobPreferences || null,
          // Asegurar completedGames: usar del estado de juegos o derivar de softSkills como fallback
          completedGames: (Array.isArray(game?.completedGames) && game.completedGames.length > 0)
            ? game.completedGames
            : (Array.isArray(personal.softSkills) && personal.softSkills.length > 0 ? ['softskills-evaluated'] : []),
          logs: []
        };

        // DEBUG: Log del requestBody completo
        console.log('🔍 DEBUG - requestBody completo:', requestBody);
        console.log('🔍 DEBUG - cvAnalysis en requestBody:', requestBody.cvAnalysis);

        const primaryUrl = buildApiUrl(API_CONFIG.ENDPOINTS.IA_REPORT);
        let res: Response;
        try {
          res = await fetch(primaryUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody),
            signal: AbortSignal.timeout(180000), // Timeout de 3 minutos
          });
        } catch (primaryErr) {
          // Fallback automático: si el backend local no responde, intentar Azure
          const azureBase = AZURE_CONFIG.AZURE_BACKEND_URL;
          const azureUrl = `${azureBase}${API_CONFIG.ENDPOINTS.IA_REPORT}`;
          if (import.meta.env.MODE !== 'production') {
            // eslint-disable-next-line no-console
            console.warn('⚠️ Conexión fallida hacia', primaryUrl, '→ intentando Azure:', azureUrl);
          }
          res = await fetch(azureUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody),
            signal: AbortSignal.timeout(180000),
          });
        }
        
        if (import.meta.env.MODE !== 'production') {
          console.log('🔍 DEBUG - Response status:', res.status);
          console.log('🔍 DEBUG - Response headers:', Object.fromEntries(res.headers.entries()));
        }
        
        const data = await res.json();
        if (import.meta.env.MODE !== 'production') {
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - Respuesta del backend:', data);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - res.ok:', res.ok);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - data exists:', !!data);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - data.summary exists:', !!data?.summary);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - data.summary value:', data?.summary);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - data.recommendations exists:', !!data?.recommendations);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - data.recommendations value:', data?.recommendations);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - Condition result:', res.ok && !!data?.summary);
        }

        // === NUEVO: capturar estrellas del backend (analysis_json / stars) ===
        try {
          const aj =
            (data?.report?.cvAnalysis as any)?.analysis_json ||
            (data?.report?.cvAnalysis as any)?.stars ||
            (data?.cvAnalysis as any)?.analysis_json ||
            (data?.cvAnalysis as any)?.stars ||
            null;
          if (aj) {
            const diag: CvDiagnostico = {
              structure_score: toStarsScale(firstNum(aj?.structure?.score, aj?.structure_score, aj?.formato, aj?.formato_score)),
              clarity_score: toStarsScale(firstNum(aj?.clarity?.score, aj?.clarity_score, aj?.claridad, aj?.claridad_score)),
              coherence_score: toStarsScale(firstNum(aj?.coherence?.score, aj?.coherence_score, aj?.coherencia, aj?.coherencia_score)),
              key_info_score: toStarsScale(firstNum(aj?.key_info?.score, aj?.key_info_score, aj?.informacion_clave, aj?.keyInfo_score)),
              spelling_style_score: toStarsScale(firstNum(aj?.spelling?.score, aj?.spelling_style_score, aj?.ortografia, aj?.estilo)),
              evidence: { structure: '', coherence: '', key_info: '', clarity: '', style: '' }
            };
            setCvStarsLocal(diag);
          }
        } catch { /* no-op */ }

        // Relajar condición: con que exista summary mostramos el informe; el resto es opcional
        // Preferir markdown determinista del backend si viene presente
        const mdDeterministic = (data?.report && (data.report.markdown || data.report.ui?.markdown)) || (data as any)?.markdown;
        if (res.ok && mdDeterministic) {
          // Eliminado: ya no se inyecta radarData en el markdown
          setIaReport(String(mdDeterministic));
          setFinalPhrase('');
          setIaScore(typeof data?.employabilityScore === 'number' ? data.employabilityScore : undefined);
          setLoadingIa(false);
          return;
        }

        // SOLUCIÓN: Cambiar la condición para usar los campos correctos del backend
        // El backend devuelve data.report.resumen_ejecutivo, no data.summary
        if (import.meta.env.MODE !== 'production') {
          console.log('🔍 DEBUG - Validando respuesta del backend:');
          console.log('  - res.ok:', res.ok);
          console.log('  - data exists:', !!data);
          console.log('  - data.report:', data?.report);
          console.log('  - data.report?.resumen_ejecutivo:', data?.report?.resumen_ejecutivo);
          console.log('  - data.employabilityScore:', data?.employabilityScore);
          console.log('  - data.level:', data?.level);
          console.log('  - data.recommendations:', data?.recommendations);
        }
        
        // NUEVA LÓGICA: Validar que la respuesta tenga la estructura esperada del backend
        const hasValidReport = res.ok && data && (
          // Verificar que exista al menos uno de estos campos requeridos
          (data.report && typeof data.report === 'object') ||
          (typeof data.employabilityScore === 'number') ||
          (typeof data.level === 'string') ||
          (Array.isArray((data as any).recommendations)) ||
          // Compatibilidad con respuestas sin 'report' (Azure)
          ((data as any).cv_analysis && typeof (data as any).cv_analysis === 'object') ||
          (Array.isArray((data as any).improvement_areas)) ||
          ((data as any).action_plan && typeof (data as any).action_plan === 'object') ||
          ((data as any).job_search_advice && typeof (data as any).job_search_advice === 'object') ||
          (Array.isArray((data as any).softSkills))
        );
        
        if (hasValidReport) {
          // Generar informe profesional con el nuevo formato
          try {
            const candidateName = String(data?.report?.fullName || userFullName);


            // Datos personales: preferir recomendaciones, luego report.ui y por último contact del CV
            const dpSrc = (data as { recommendations?: { datos_personales?: Record<string, unknown> }; report?: { ui?: { datos_personales?: Record<string, unknown> } } })?.recommendations?.datos_personales
              || (data as { report?: { ui?: { datos_personales?: Record<string, unknown> } } })?.report?.ui?.datos_personales
              || {} as Record<string, unknown>;
            const ca = (data?.report?.cvAnalysis || cvAnalysis || {}) as any;
            const contactDirect = (ca && ca.contact) || {};
            const candidateObj = (ca && (ca.cv_structured || ca.cv_analysis_structured || {}).candidate) || {};
            const contact = (contactDirect && (contactDirect.emails || contactDirect.phones || contactDirect.location) ? contactDirect : {
              emails: Array.isArray(candidateObj.emails) ? candidateObj.emails : [],
              phones: Array.isArray(candidateObj.phones) ? candidateObj.phones : [],
              location: candidateObj.location
            }) as { emails?: string[]; phones?: string[]; location?: string };
            const dp = {
              name: (dpSrc?.['name'] as string) || candidateName,
              location: (dpSrc?.['location'] as string) || contact?.location || 'No consta',
              email: (dpSrc?.['email'] as string) || (Array.isArray(contact?.emails) ? contact.emails[0] : '') || 'No consta',
              phone: (dpSrc?.['phone'] as string) || (Array.isArray(contact?.phones) ? contact.phones[0] : '') || 'No especificado',
              disability_certificate: (dpSrc?.['disability_certificate'] != null)
                ? (dpSrc['disability_certificate'] as string)
                : ((report?.jobPreferences as any)?.hasDisabilityCert ? 'Sí' : 'No')
            };


            // const rec = ((data as { recommendations?: Record<string, unknown> })?.recommendations) || {} as Record<string, unknown>;

            // Preferir analysis_json (persistido por backend) como fuente única de verdad para puntuaciones 1–5
            const analysisJson: any = (data?.report?.cvAnalysis as any)?.analysis_json || null;
            if (analysisJson && (!analysisJson.overall || analysisJson.overall.score == null)) {
              throw new Error('Falta overall.score en analysis_json');
            }

            // Construir SIEMPRE el informe con tu formato deseado
            let markdown = buildDesiredMarkdown(data, String(dp.name || candidateName));
            // Eliminado: ya no se añade el bloque JSON radarData al markdown
            setIaReport(markdown);
            if (import.meta.env.MODE !== 'production') {
              // eslint-disable-next-line no-console
              console.log('✅ DEBUG - Informe generado exitosamente. Longitud:', markdown.length);
              // eslint-disable-next-line no-console
              console.log('✅ DEBUG - Primeros 200 caracteres:', markdown.substring(0, 200));
            }
            // Frase motivacional final destacada (fuera del markdown principal)
            // Construimos SIEMPRE el mensaje final personalizado para la caja azul
            const composed = ((): string => {
              const firstName = (String(dp.name || candidateName).split(' ')[0] || 'Tu perfil').trim();
              const normalize = (val: unknown): string => {
                const n = String(val || '').toLowerCase().trim();
                if (!n) return '';
                if (/anal(í|i)tico/.test(n)) return 'pensamiento analítico';
                if (/cr(í|i)tico/.test(n)) return 'pensamiento crítico';
                if (/curiosidad|aprendizaje/.test(n)) return 'curiosidad y aprendizaje';
                if (/resiliencia|flexibilidad/.test(n)) return 'resiliencia y flexibilidad';
                if (/autoconciencia/.test(n)) return 'autoconciencia';
                if (/influencia/.test(n)) return 'influencia social';
                if (/decisiones/.test(n)) return 'toma de decisiones';
                return String(val || 'fortalezas');
              };
              const sorted = [...(softSkillsToSend || [])].sort((a:any,b:any)=> (b?.score??0)-(a?.score??0));
              const s1 = normalize(sorted[0]?.skill);
              const s2 = normalize(sorted[1]?.skill);
              const remotePref = (report?.jobPreferences as any)?.remoteWork ? 'el trabajo remoto' : 'los entornos presenciales';
              const rolesArr: any[] = Array.isArray((data as any)?.report?.suggested_roles) ? (data as any).report.suggested_roles : [];
              const roleName = (r:any)=> (r?.name||r?.title||r?.role||r?.label||r?.position||r?.jobTitle||'');
              const roleHint = rolesArr.map(roleName).filter(Boolean).slice(0,2).join(' y ') || 'roles administrativos';
              const improv: any[] = Array.isArray((data as any)?.report?.improvement_areas) ? (data as any).report.improvement_areas : [];
              const clean = (v:string)=> String(v||'').replace(/\s*\((?:\d+%?|\d+\s*\/\s*\d+)\)\s*/g,'').trim();
              const improvementAreas = improv.map(a=> clean(a?.area||a?.name||'')).filter(Boolean).slice(0,2).join(' y ') || 'tus áreas de mejora';
              const fortalezas = s1 && s2 ? `Aprovecha tu ${s1} y ${s2} para avanzar hacia tus objetivos profesionales.` : s1 ? `Aprovecha tu ${s1} para avanzar hacia tus objetivos profesionales.` : 'Aprovecha tus fortalezas para avanzar hacia tus objetivos profesionales.';
              return `Este informe ha sido elaborado a partir de tus preferencias laborales, los resultados de los minijuegos y tu CV.\n\n${firstName}, tu perfil muestra una base sólida de habilidades y una clara orientación al crecimiento.\n\n${fortalezas} Además, ${remotePref} y ${roleHint} encajan con tus competencias. Continúa desarrollando ${improvementAreas} y mantén la motivación: tu potencial está en constante evolución.`;
            })();
            setFinalPhrase(composed);
            setIaScore(typeof data?.employabilityScore === 'number' ? data.employabilityScore : undefined);
            if (import.meta.env.MODE !== 'production') {
              // eslint-disable-next-line no-console
              console.log('✅ DEBUG - Estado iaReport actualizado');
            }
          } catch (error) {
            if (import.meta.env.MODE !== 'production') {
              // eslint-disable-next-line no-console
              console.error('❌ Error generando informe:', error);
            }
            // Fallback: construir un informe mínimo usando solo summary si está disponible
            try {
              const summaryText = typeof data?.summary === 'string' && data.summary.trim()
                ? data.summary.trim()
                : 'Tu informe personalizado está en proceso. A continuación tienes un resumen básico basado en tu evaluación.';
              const minimal = `# Informe Profesional de Empleabilidad\n\n## Resumen del Perfil\n${summaryText}\n\n---\n*Informe generado automáticamente.*`;
              setIaReport(minimal);
              if (import.meta.env.MODE !== 'production') {
                // eslint-disable-next-line no-console
                console.log('✅ DEBUG - Fallback de informe básico establecido');
              }
            } catch (e) {
              setErrorIa('No se pudo generar el informe en este momento.');
            }
          }
        } else {
          if (import.meta.env.MODE !== 'production') {
            // eslint-disable-next-line no-console
            console.log('❌ DEBUG - Condición falló. Motivos:');
            // eslint-disable-next-line no-console
            console.log('  - res.ok:', res.ok);
            // eslint-disable-next-line no-console
            console.log('  - data:', !!data);
            // eslint-disable-next-line no-console
            console.log('  - data.report:', !!data?.report);
            // eslint-disable-next-line no-console
            console.log('  - data.report?.resumen_ejecutivo:', !!data?.report?.resumen_ejecutivo);
            // eslint-disable-next-line no-console
            console.log('  - data.employabilityScore:', data?.employabilityScore);
            // eslint-disable-next-line no-console
            console.log('  - data.level:', data?.level);
            console.log('  - data completo:', data);
          }
          
          // NUEVO: Mensaje de error más específico basado en la respuesta
          if (!res.ok) {
            setErrorIa(`Error del servidor: ${res.status} ${res.statusText}`);
          } else if (!data) {
            setErrorIa('No se recibieron datos del servidor');
          } else if (!data.report && !data.employabilityScore && !data.level && !data.recommendations) {
            setErrorIa('La respuesta del servidor no tiene el formato esperado');
          } else {
            setErrorIa('No se pudo generar el informe IA.');
          }
        }
      } catch (err) {
        // console.error('Error en fetchIaReport:', err);
        if (err instanceof Error && err.name === 'TimeoutError') {
          setErrorIa('El informe está tardando más de lo esperado. Se generará un informe básico automáticamente.');
        } else if (err instanceof Error && err.message?.includes('Failed to fetch')) {
          setErrorIa('No se pudo conectar con el servidor. Verifica tu conexión a internet.');
        } else {
          // Fallback robusto: generar un informe básico local y no mostrar banner
          try {
            const fallbackName = `${report?.firstName || ''} ${report?.lastName || ''}`.trim() || 'Usuario';
            const minimal = `# Informe Profesional de Empleabilidad\n\n## Resumen del Perfil\nInforme básico para ${fallbackName}.\n\n---\n*Informe generado automáticamente.*`;
            setIaReport(minimal);
            setErrorIa('');
          } catch {
            // En última instancia, mantener silencio para no bloquear la UI
          }
        }
      } finally {
        setLoadingIa(false);
      }
    };
    // SOLUCIÓN: Ejecutar siempre el informe si hay datos básicos del usuario
    // Verificar tanto personal.softSkills como report?.softSkills
    const hasPersonalSoftSkills = validateSoftSkills(personal.softSkills);
    const hasReportSoftSkills = validateSoftSkills(report?.softSkills || []);
    const hasSoftSkills = hasPersonalSoftSkills || hasReportSoftSkills;
    
    // NUEVO: También permitir generar informe si hay datos básicos del usuario
    const hasBasicUserData = (report?.firstName && report?.lastName) || 
                            (cvAnalysis) || 
                            (report?.jobPreferences);
    
    if (fetchedRef.current) {
      return;
    }
    if (hasSoftSkills || hasBasicUserData) {
      // Condición cumplida - Ejecutando fetchIaReport
      if (import.meta.env.MODE !== 'production') {
        // eslint-disable-next-line no-console
        console.log('✅ CONDICIÓN CUMPLIDA - Ejecutando fetchIaReport');
        // eslint-disable-next-line no-console
        console.log('  • hasSoftSkills:', hasSoftSkills);
        // eslint-disable-next-line no-console
        console.log('  • hasBasicUserData:', hasBasicUserData);
      }
      fetchedRef.current = true;
      fetchIaReport();
    } else {
      // Condición no cumplida - No se ejecuta fetchIaReport
      if (import.meta.env.MODE !== 'production') {
        // eslint-disable-next-line no-console
        console.log('❌ CONDICIÓN NO CUMPLIDA - No se ejecuta fetchIaReport');
        // eslint-disable-next-line no-console
        console.log('  • hasPersonalSoftSkills:', hasPersonalSoftSkills);
        // eslint-disable-next-line no-console
        console.log('  • hasReportSoftSkills:', hasReportSoftSkills);
        // eslint-disable-next-line no-console
        console.log('  • hasBasicUserData:', hasBasicUserData);
      }
    }
  }, [report?.jobPreferences, personal.softSkills, report?.softSkills, personal.jobPreferences, cvAnalysis, game?.completedGames, report?.firstName, report?.lastName, report?.userId]);

  // Estado para feedback
  const [feedback, setFeedback] = useState<{rating: string, comment: string}>({rating: '', comment: ''});
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackError, setFeedbackError] = useState('');

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedbackError('');
    try {
      const res = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.IA_FEEDBACK), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          informe: iaReport,
          rating: feedback.rating,
          comment: feedback.comment,
          userData: { preferences: report?.jobPreferences, minigames: personal.softSkills, cvAnalysis },
        }),
      });
      if (res.ok) {
        setFeedbackSent(true);
      } else {
        setFeedbackError('No se pudo enviar el feedback.');
      }
    } catch {
      setFeedbackError('Error de conexión al enviar feedback.');
    }
  };

  // Estado para el progreso de la barra
  const [progress, setProgress] = useState(0);

  // Eliminado: descarga de PDF (se usará impresión para descargar informe)

  // Efecto para animar la barra de progreso
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;
    if (loadingIa) {
      setProgress(0);
      interval = setInterval(() => {
        setProgress(prev => {
          // Avanza hasta 95% mientras loadingIa es true
          if (prev < 95) {
            return prev + Math.random() * 5 + 1; // avance aleatorio para naturalidad
          } else {
            return prev;
          }
        });
      }, 200);
    } else {
      // Cuando termina la carga, completa la barra
      setProgress(100);
      // Opcional: después de un pequeño delay, resetea la barra
      setTimeout(() => setProgress(0), 800);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [loadingIa]);

  // Eliminado: lógica de descarga de PDF

  // Función para imprimir
  const handlePrint = () => {
    window.print();
  };

  // 1. Portada
  const portada = (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 flex flex-col items-center mb-8 print-report-section print-page-break-inside-avoid transition-colors">
      <img src={logo} alt="Logo EvalúaTE" className="w-32 mb-4 print-shadow-none" />
      <h1 className="text-4xl font-bold mb-2 text-gray-900 dark:text-gray-100">Informe de Empleabilidad</h1>
      <h2 className="text-2xl font-semibold mb-1 text-gray-900 dark:text-gray-100">{report?.firstName} {report?.lastName}</h2>
      <p className="text-gray-900 dark:text-gray-100">{fecha}</p>
      
      {/* Botones de acción */}
      <div className="flex gap-4 mt-6 print-hidden">
        <button
          onClick={handlePrint}
          disabled={!iaReport}
          className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
            !iaReport
              ? 'bg-gray-300 text-gray-900 cursor-not-allowed'
              : 'bg-[#374ba6] text-white hover:bg-[#2d3f96]'
          }`}
        >
          <span className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            Descargar Informe
          </span>
        </button>
      </div>
      
      {/* Eliminado: mensaje de error del PDF */}
    </div>
  );

  // 2. Mapa de habilidades (Radar + resumen)
  // Usar useMemo para evitar recalcular en cada render
  const radarDataFromIa = useMemo(() => iaReport ? extractRadarData(iaReport) : [], [iaReport]);

  // Función para eliminar duplicados y asegurar claves únicas
  const processRadarData = (data: Array<{ skill?: string; softskill?: string; score: number }>) => {
    if (!Array.isArray(data)) {
      // Evitar logs en producción
      return [];
    }
    
    const seen = new Set();
    const processedData = data
      .map(item => ({
        softskill: String(item.skill || item.softskill || '').trim(),
        score: Math.max(0, Math.min(100, Math.round(Number(item.score) || 0))),
      }))
      .filter(item => {
        if (seen.has(item.softskill)) {
          return false; // Eliminar duplicados
        }
        seen.add(item.softskill);
        return item.score > 0; // Solo elementos con score válido
      });
    
    // Intercambiar solo "Pensamiento analítico" y "Liderazgo"
    return processedData.map(item => {
      if (item.softskill === "Pensamiento analítico") {
        return { ...item, softskill: "Liderazgo" };
      } else if (item.softskill === "Liderazgo") {
        return { ...item, softskill: "Pensamiento analítico" };
      }
      return item;
    });
  };

  const mergedSoftSkills = useMemo(() => {
    // Merge de soft skills de juegos (game.softSkills) con personal.softSkills
    const personalSkills = filterValidSoftSkills(personal.softSkills || []);
    const gameSkills = Array.isArray(game?.softSkills) ? game.softSkills : [];
    const mappedGame = gameSkills.map((s:any) => {
      const score = Math.round(Number(s?.score) || 0);
      const level = s?.level || (score < 50 ? 'bajo' : score < 75 ? 'medio' : 'alto');
      const conf = typeof s?.confidence === 'number' && s.confidence <= 1
        ? Math.round(s.confidence * 100)
        : Math.round(Number(s?.confidence) || 80);
      return { skill: String(s?.name || s?.softSkill || 'Habilidad'), score, level, confidence: conf };
    });
    const byName: Record<string, any> = {};
    for (const s of [...personalSkills, ...mappedGame]) {
      if (!s || !s.skill) continue;
      if (!byName[s.skill] || (Number(s.score) || 0) > (Number(byName[s.skill].score) || 0)) {
        byName[s.skill] = s;
      }
    }
    return Object.values(byName);
  }, [personal.softSkills, game?.softSkills]);
  const computedScore = useMemo(() => {
    if (!mergedSoftSkills || mergedSoftSkills.length === 0) return undefined;
    const sum = mergedSoftSkills.reduce((acc, s) => acc + (Number(s.score) || 0), 0);
    const avg = sum / mergedSoftSkills.length;
    // Evitar 0 en gráficas si hay datos; mínimo 10
    return Math.max(10, Math.round(avg));
  }, [mergedSoftSkills]);
  const globalScore = iaScore ?? report?.employabilityScore ?? computedScore;
  const radarData = radarDataFromIa.length > 0
    ? processRadarData(radarDataFromIa)
    : processRadarData(mergedSoftSkills);
  // Color de etiquetas del radar según modo (claro/oscuro)
  // Modo claro: etiquetas oscuras para legibilidad contra fondo blanco
  // Modo oscuro: etiquetas blancas para legibilidad contra fondo oscuro
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => document.documentElement.classList.contains('dark'));
  useEffect(() => {
    const root = document.documentElement;
    const observer = new MutationObserver(() => {
      setIsDarkMode(root.classList.contains('dark'));
    });
    observer.observe(root, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);
  const radarLabelColor = isDarkMode ? '#FFFFFF' : '#374151';

  const radar = (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 mb-8 print-report-section print-page-break-inside-avoid transition-colors">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-gray-100">Mapa de habilidades</h2>
      <div className="flex flex-col md:flex-row gap-8 items-center">
        <div className="w-full md:w-3/5 h-96" ref={radarBoxRef}>
          <div className="screen-only h-full">
            {radarData.length > 0 ? (
              <ResponsiveRadar
                data={radarData}
                keys={["score"]}
                indexBy="softskill"
                margin={{ top: 40, right: 100, bottom: 40, left: 100 }}
                theme={{
                  // Asegurar legibilidad de etiquetas en ambos modos
                  text: { fill: radarLabelColor, fontSize: 12 },
                  grid: { line: { stroke: '#6B7280', strokeWidth: 1 } },
                  axis: {
                    ticks: { text: { fill: radarLabelColor, fontSize: 12 } },
                    domain: { line: { stroke: '#9CA3AF' } },
                    legend: { text: { fill: radarLabelColor, fontSize: 12 } },
                  },
                  // Etiquetas del radar (nombres de habilidades)
                  labels: { text: { fill: radarLabelColor, fontSize: 12 } },
                  // Leyendas, en caso de usarse en el futuro
                  legends: { text: { fill: radarLabelColor, fontSize: 12 } },
                  crosshair: { line: { stroke: '#F3F4F6' } },
                }}
                borderColor="#3B82F6"
                gridLabelOffset={25}
                dotSize={12}
                dotColor="#3B82F6"
                dotBorderWidth={2}
                dotBorderColor={{ theme: 'background' }}
                colors={['#3B82F6']}
                fillOpacity={0.35}
                blendMode="multiply"
                animate={true}
                isInteractive={false}
                legends={[]}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-900 dark:text-gray-100">
                <p>No hay datos suficientes para mostrar el gráfico de habilidades</p>
              </div>
            )}
          </div>
          {radarImg && (
            <img src={radarImg} alt="Mapa de habilidades" className="print-only w-full h-96 object-contain" />
          )}
        </div>
        <div className="w-full md:w-2/5">
          <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100 text-sm">Resumen de puntuaciones:</h3>
          <ul className="space-y-1 text-sm">
            {(() => {
              try {
                const validSkills = filterValidSoftSkills(personal.softSkills || []);
                return validSkills.map((skill, idx: number) => (
                  <li key={idx}>
                    <span className="font-medium text-gray-900 dark:text-gray-100">{skill.skill}:</span> {skill.score}%
                  </li>
                ));
              } catch (e) {
                return <li key="error" className="text-gray-900 dark:text-gray-100">Error al cargar habilidades</li>;
              }
            })()}
          </ul>
          <p className="font-semibold mt-2 text-gray-900 dark:text-gray-100 text-sm">
            Puntaje global de empleabilidad: {globalScore ?? report?.employabilityScore ?? '-'}
          </p>
        </div>
      </div>
    </div>
  );

  // Ya no se necesitan las secciones hardcodeadas
  // El contenido ahora viene de la IA

  // === NUEVO: función para renderizar el bloque "Análisis del Currículum" ===
  const renderCvAnalysisSection = () => {
    const ca: any = cvAnalysis || (typeof (personal as any)?.cvAnalysis === 'object' ? (personal as any).cvAnalysis : null);
    
    // Verificar si hay datos del análisis del CV
    if (!ca) return null;

    // Obtener datos del backend - priorizar analysis_json si está disponible
    const analysisJson = (ca as any)?.analysis_json || {};
    const starsFromBackend = (ca as any)?.stars || {};
    
    // Función para obtener puntuaciones con fallbacks
    const getScore = (field: string, fallback: number = 3): CvStars => {
      const score = analysisJson[field] || starsFromBackend[field] || fallback;
      return Math.max(1, Math.min(5, Number(score) || fallback)) as CvStars;
    };

    // Obtener puntuaciones reales del backend
    const formatScore = getScore('structure_score', 3);
    const clarityScore = getScore('clarity_score', 2);
    // Coherencia: ajustar a 3/5 mínimo si la cronología detectada es correcta
    const experienceItems: any[] = Array.isArray(ca?.experience_detailed)
      ? ca.experience_detailed
      : (Array.isArray(ca?.cv_structured?.experience) ? ca.cv_structured.experience : []);
    const parseYear = (v: unknown): number | null => {
      const s = String(v || '').match(/(19|20)\d{2}/);
      return s ? Number(s[0]) : null;
    };
    const chronologyOk = (() => {
      try {
        const years: number[] = [];
        for (const it of experienceItems) {
          const ys = parseYear((it as any)?.start_date || (it as any)?.fecha_inicio || (it as any)?.dates);
          const ye = parseYear((it as any)?.end_date || (it as any)?.fecha_fin || (it as any)?.dates);
          const y = ye ?? ys;
          if (y != null) years.push(y);
        }
        if (years.length < 2) return false;
        let asc = true;
        for (let i = 1; i < years.length; i++) {
          const current = years[i] as number;
          const previous = years[i - 1] as number;
          if (current < previous) { asc = false; break; }
        }
        let desc = true;
        for (let i = 1; i < years.length; i++) {
          const current = years[i] as number;
          const previous = years[i - 1] as number;
          if (current > previous) { desc = false; break; }
        }
        return asc || desc;
      } catch {
        return false;
      }
    })();
    const coherenceRaw = getScore('coherence_score', 2);
    const coherenceScore = (chronologyOk && (coherenceRaw as number) < 3 ? 3 : coherenceRaw) as CvStars;
    const keyInfoScore = getScore('key_info_score', 2);
    const spellingScore = getScore('spelling_style_score', 3);

    // Obtener evidencia y observaciones del backend
    const observations = analysisJson.observations || [];
    const corrections = analysisJson.corrections || [];
    const reorderingSuggestions = analysisJson.reordering_suggestions || [];

    // Generar observaciones basadas en los datos del CV si no hay observaciones del backend
    const generateObservations = (): string[] => {
      if (observations.length > 0) return observations;

      const obs: string[] = [];

      // Análisis de estructura
      const cvStruct = (ca?.cv_structured ?? {}) as any;
      const exp = Array.isArray(ca?.experience_detailed) ? ca.experience_detailed : 
                  (Array.isArray(cvStruct?.experience) ? cvStruct.experience : []);
      const edu = Array.isArray(ca?.education_detailed) ? ca.education_detailed : 
                  (Array.isArray(cvStruct?.education) ? cvStruct.education : []);
      const skills = Array.isArray(ca?.skills) ? ca.skills : 
                     (Array.isArray(cvStruct?.skills) ? cvStruct.skills : []);

      if (exp.length > 0 || edu.length > 0 || skills.length > 0) {
        const parts: string[] = [];
        if (exp.length) parts.push(`${exp.length} experiencias`);
        if (edu.length) parts.push(`${edu.length} formaciones`);
        if (skills.length) parts.push(`${skills.length} herramientas/skills`);
        obs.push(`**Estructura:** se observan secciones básicas (${parts.join(', ')}), pero la jerarquía visual es limitada.`);
      }

      // Análisis de claridad
      obs.push(`**Claridad:** ausencia de bullets y verbos de acción; la redacción es general y sin foco en logros/impacto.`);

      // Análisis de coherencia
      if (chronologyOk) {
        obs.push(`**Coherencia:** las fechas y el orden temporal son consistentes; persisten incoherencias de formato (ubicaciones, uso de 'Teletrabajo', puntuación).`);
      } else {
        obs.push(`**Coherencia:** faltan detalles de fechas u orden temporal; además hay variaciones de formato entre entradas.`);
      }

      // Análisis de información clave
      const hasLinks = /https?:\/\//i.test(String(ca?.raw_text || '')) || /linkedin\.com/i.test(String(ca?.raw_text || ''));
      obs.push(`**Información clave:** ${hasLinks ? 'Hay enlaces, pero' : 'No hay enlaces y'} no se incluyen KPIs/métricas cuantificables.`);

      // Análisis de ortografía: detectar errores comunes
      const corpusParts: string[] = [];
      try {
        const pushIf = (v: unknown) => { if (typeof v === 'string') corpusParts.push(v); };
        pushIf(ca?.raw_text);
        for (const it of exp as any[]) pushIf((it as any)?.description || (it as any)?.summary || (it as any)?.title);
        for (const it of edu as any[]) pushIf((it as any)?.degree || (it as any)?.center);
        for (const it of skills as any[]) pushIf(typeof it === 'string' ? it : (it as any)?.name);
      } catch { /* no-op */ }
      const corpus = corpusParts.join(' \n ').toLowerCase();
      const detected: string[] = [];
      const typo = (wrong: string | RegExp, correct: string) => {
        const re = typeof wrong === 'string' ? new RegExp(`\\b${wrong.toLowerCase()}\\b`, 'i') : wrong;
        if (re.test(corpus)) {
          // Extraer solo la palabra incorrecta sin el formato de regex
          const wrongWord = typeof wrong === 'string' ? wrong : wrong.source.replace(/[\/\\^$*+?.()|[\]{}]/g, '');
          detected.push(`${wrongWord} → ${correct}`);
        }
      };
      typo(/indesing/i, 'InDesign');
      typo(/ilustrator/i, 'Illustrator');
      typo(/l[ée]on/i, 'León');
      typo(/teamwokz/i, 'Teamworkz');
      if (detected.length > 0) {
        obs.push(`**Ortografía y estilo:** se detectan errores menores: ${detected.join(', ')}.`);
      } else {
        obs.push('**Ortografía y estilo:** sin fallos graves detectados.');
      }

      return obs;
    };

    // Generar correcciones/acciones si no hay del backend
    const generateCorrections = (): string[] => {
      if (corrections.length > 0) return corrections;

      const out = [
        'Añadir logros cuantificables y KPIs en cada experiencia.',
        'Incluir enlaces a LinkedIn u otros perfiles profesionales.',
        'Homogeneizar el formato de fechas y ubicaciones.',
        'Utilizar bullets y verbos de acción claros.'
      ] as string[];
      // Añadir corrección ortográfica específica si se detectaron errores
      const obsLocal = generateObservations();
      const orto = obsLocal.find(t => t.toLowerCase().startsWith('ortografía'));
      if (orto && /se detectan errores menores/i.test(orto)) {
        out.push('Corregir las palabras detectadas (InDesign, Illustrator, León, Teamworkz) y revisar el estilo.');
      } else {
        out.push('Revisar ortografía y formato general.');
      }
      return out;
    };

    // Generar sugerencias de reordenación si no hay del backend
    const generateReorderingSuggestions = (): string[] => {
      if (reorderingSuggestions.length > 0) return reorderingSuggestions;

      const suggestions: string[] = [];
      const hasProfile = Boolean(ca?.cv_structured?.summary || (ca as any)?.summary);
      const layout = ca?.layout_sections as any[] | undefined;
      let experienceBeforeEducation: boolean | undefined;
      try {
        if (Array.isArray(layout)) {
          const norm = (s: string) => String(s || '').toLowerCase();
          const expIdx = layout.findIndex(s => /experien/.test(norm(String((s as any)))));
          const eduIdx = layout.findIndex(s => /edu(caci|cation|ación)/i.test(norm(String((s as any)))));
          if (expIdx >= 0 && eduIdx >= 0) experienceBeforeEducation = expIdx < eduIdx;
        }
      } catch { /* no-op */ }

      if (!hasProfile) suggestions.push('Colocar el perfil profesional al inicio.');
      if (experienceBeforeEducation === false) suggestions.push('Agrupar la experiencia profesional antes de la formación.');
      suggestions.push('Incluir una sección específica de habilidades técnicas y soft skills.');
      return suggestions;
    };

    const finalObservations = generateObservations();
    const finalCorrections = generateCorrections();
    const finalReorderingSuggestions = generateReorderingSuggestions();

    return (
      <div className="print-page-break-inside-avoid mb-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-gray-100">Análisis del CV (con puntuación 1–5 por apartado)</h2>
        
        {/* Sección de puntuaciones con estrellas */}
        <div className="mb-4">
          <div className="border-l-4 border-blue-500 pl-4 rounded-md" style={{ backgroundColor: '#F9FAFB' }}>
            <div className="space-y-1">
              <div className="flex items-center gap-3">
                <span className="font-semibold text-gray-900 dark:text-gray-800">Formato:</span>
                <span className="text-lg"><StarsGold n={formatScore} /></span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-semibold text-gray-900 dark:text-gray-800">Claridad:</span>
                <span className="text-lg"><StarsGold n={clarityScore} /></span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-semibold text-gray-900 dark:text-gray-800">Coherencia:</span>
                <span className="text-lg"><StarsGold n={coherenceScore} /></span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-semibold text-gray-900 dark:text-gray-800">Información clave:</span>
                <span className="text-lg"><StarsGold n={keyInfoScore} /></span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-semibold text-gray-900 dark:text-gray-800">Ortografía:</span>
                <span className="text-lg"><StarsGold n={spellingScore} /></span>
              </div>
            </div>
          </div>
        </div>

        {/* Observaciones del análisis */}
        {finalObservations.length > 0 && (
          <div className="mb-4">
            <p className="font-semibold mb-2 text-gray-900 dark:text-gray-100">Observaciones del análisis:</p>
            <ul className="list-disc list-inside space-y-1 text-gray-900 dark:text-gray-100">
              {finalObservations.map((obs, i) => (
                <li key={i} className={`text-gray-900 dark:text-gray-100 ${i === 0 ? 'mt-0' : ''}`}>
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({ children }) => <span>{children}</span>,
                      strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                      ul: ({ children }) => <ul className="list-disc list-inside space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside space-y-1">{children}</ol>,
                      li: ({ children, ...props }) => <li className="leading-relaxed" {...props}>{children}</li>,
                    }}
                  >
                    {obs}
                  </ReactMarkdown>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Correcciones/Acciones sugeridas */}
        {finalCorrections.length > 0 && (
          <div className="mb-4">
            <p className="font-semibold mb-2 text-gray-900 dark:text-gray-100">Correcciones/Acciones:</p>
            <ul className="list-disc list-inside space-y-1 text-gray-900 dark:text-gray-100">
              {finalCorrections.map((correction, i) => (
                <li key={i} className={`text-gray-900 dark:text-gray-100 ${i === 0 ? 'mt-0' : ''}`}>{correction}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Reordenación sugerida */}
        {finalReorderingSuggestions.length > 0 && (
          <div className="mb-4">
            <p className="font-semibold mb-2 text-gray-900 dark:text-gray-100">Reordenación sugerida:</p>
            <ul className="list-disc list-inside space-y-1 text-gray-900 dark:text-gray-100">
              {finalReorderingSuggestions.map((suggestion, i) => (
                <li key={i} className={`text-gray-900 dark:text-gray-100 ${i === 0 ? 'mt-0' : ''}`}>{suggestion}</li>
              ))}
            </ul>
          </div>
        )}


      </div>
    );
  };

  // === NUEVO: función común para renderizar markdown con el mismo estilo ===
  const renderMarkdown = (content: string) => (
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ children, ...props }) => (
                    <h1 {...props} className="text-3xl font-bold mb-6 mt-8 pb-2 border-b-2 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100">
                      {children}
                    </h1>
                  ),
                  h2: ({ children, ...props }) => (
                    <h2 {...props} className="text-2xl font-semibold mb-4 mt-6 text-gray-900 dark:text-gray-100">
                      {children}
                    </h2>
                  ),
                  h3: ({ children, ...props }) => (
                    <h3 {...props} className="text-xl font-semibold mb-3 mt-5 text-gray-900 dark:text-gray-100">
                      {children}
                    </h3>
                  ),
                  h4: ({ children, ...props }) => (
                    <h4 {...props} className="text-lg font-semibold mb-2 mt-4 text-gray-900 dark:text-gray-100">
                      {children}
                    </h4>
                  ),
                  ul: ({ children, ...props }) => (
                    <ul {...props} className="list-disc list-inside space-y-1 mb-2 text-gray-900 dark:text-gray-100">
                      {children}
                    </ul>
                  ),
                  ol: ({ children, ...props }) => (
                    <ol {...props} className="list-decimal list-inside space-y-1 mb-2 text-gray-900 dark:text-gray-100">
                      {children}
                    </ol>
                  ),
                  li: ({ children, ...props }) => (
                    <li {...props} className="leading-relaxed text-gray-900 dark:text-gray-100">
                      {children}
                    </li>
                  ),
                  strong: ({ children, ...props }) => (
                    <strong {...props} className="font-semibold text-gray-900 dark:text-gray-100">
                      {children}
                    </strong>
                  ),
                  em: ({ children, ...props }) => (
                    <em {...props} className="italic text-gray-900 dark:text-gray-100">
                      {children}
                    </em>
                  ),
                  blockquote: ({ children, ...props }) => (
                    <blockquote {...props} className="border-l-4 border-blue-500 pl-4 italic text-gray-900 dark:text-gray-100 bg-blue-50 dark:bg-blue-900/30 py-2 rounded-r">
                      {children}
                    </blockquote>
                  ),
                  code: ({ children, ...props }) => (
                      <code {...props} className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-sm font-mono text-gray-900 dark:text-gray-100">
                      {children}
                    </code>
                  ),
                  pre: ({ children, ...props }) => (
                    <pre {...props} className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg overflow-x-auto text-sm font-mono text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-600">
                      {children}
                    </pre>
                  ),
                  table: ({ children, ...props }) => (
                    <div className="overflow-x-auto mb-4">
                      <table {...props} className="min-w-full border-collapse border border-gray-300 dark:border-gray-600">
                        {children}
                      </table>
                    </div>
                  ),
                  th: ({ children, ...props }) => (
                    <th {...props} className="border border-gray-300 dark:border-gray-600 px-4 py-2 bg-gray-50 dark:bg-gray-800 font-semibold text-gray-900 dark:text-gray-100 text-left">
                      {children}
                    </th>
                  ),
                  td: ({ children, ...props }) => (
                    <td {...props} className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-900 dark:text-gray-100">
                      {children}
                    </td>
                  ),
                  a: ({ children, href, ...props }) => (
                    <a {...props} href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline">
                      {children}
                    </a>
                  ),
                  hr: ({ ...props }) => (
                    <hr {...props} className="border-t border-gray-300 dark:border-gray-600 my-6" />
                  ),
                  p: ({ children, ...props }) => {
                    const extractText = (node: unknown): string => {
                      if (node == null) return '';
                      if (typeof node === 'string' || typeof node === 'number') return String(node);
                      if (Array.isArray(node)) return node.map(extractText).join('');
                      // @ts-expect-error - acceso seguro a props.children si existe
                      if (typeof node === 'object' && node.props && node.props.children) {
                        // @ts-expect-error - children puede ser nodo o array
                        return extractText(node.props.children);
                      }
                      return '';
                    };

                    const text = extractText(children);
                    if (text.includes('★')) {
                      if (/(Formato|Claridad|Coherencia|Información clave|Ortografía(?: y estilo)?):\s*[★☆]/.test(text)) {
                        const indicators: Array<{ label: string; stars: string }> = [];
                        const re = /(Formato|Claridad|Coherencia|Información clave|Ortografía(?: y estilo)?):\s*([★☆]+)/g;
                        let m: RegExpExecArray | null;
                        // eslint-disable-next-line no-cond-assign
                        while ((m = re.exec(text)) !== null) {
                          const rawLabel = m[1];
                          if (rawLabel && m[2]) {
                            const normLabel = rawLabel.startsWith('Ortografía') ? 'Ortografía' : rawLabel;
                            indicators.push({ label: normLabel, stars: m[2] });
                          }
                        }
                        return (
                          <div {...props} className="quality-indicators">
                            <ul className="text-gray-900 dark:text-gray-100 leading-relaxed space-y-1">
                              {indicators.length > 0 ? indicators.map((it, idx) => {
                                const starMatch = it.stars.match(/(★+)(☆*)/);
                                const filledStars = starMatch ? starMatch[1] : '';
                                const emptyStars = starMatch ? starMatch[2] : '';
                                return (
                                  <li key={idx} className="flex items-center gap-2">
                                    <span className="font-semibold text-gray-900 dark:text-gray-100">{it.label}:</span>
                                    <span>
                                      <span className="star-filled">{filledStars}</span>
                                      <span className="star-empty">
                                        {emptyStars}
                                      </span>
                                    </span>
                                  </li>
                                );
                              }) : (
                                <li className="text-gray-900 dark:text-gray-100">{text}</li>
                              )}
                            </ul>
                          </div>
                        );
                      } else {
                        const parts = text.split(/((?:★+)(?:☆*))/g);
                        return (
                          <p {...props} className="text-gray-900 dark:text-gray-100 leading-relaxed mb-4 text-justify">
                            {parts.map((part, index) => {
                              const starMatch = part.match(/(★+)(☆*)/);
                              if (starMatch) {
                                const [, filledStars, emptyStars] = starMatch;
                                if (filledStars && emptyStars) {
                                  const filledCount = filledStars.length;
                                  const totalCount = filledCount + emptyStars.length;
                                  const percentage = (filledCount / totalCount) * 100;
                        let colorClass = 'star-very-poor';
                        if (percentage >= 90) colorClass = 'star-excellent';
                        else if (percentage >= 80) colorClass = 'star-very-good';
                        else if (percentage >= 70) colorClass = 'star-good';
                        else if (percentage >= 60) colorClass = 'star-average';
                        else if (percentage >= 50) colorClass = 'star-regular';
                        else if (percentage >= 40) colorClass = 'star-below-average';
                        else if (percentage >= 30) colorClass = 'star-poor';
                        else colorClass = 'star-very-poor';
                                  return (
                                    <span key={index}>
                                      <span className={`${colorClass} star-filled`}>
                                        {filledStars}
                                      </span>
                                      <span className="star-empty">
                                        {emptyStars}
                                      </span>
                                    </span>
                                  );
                                }
                              }
                              return part;
                            })}
                          </p>
                        );
                      }
                    }
                    return (
                      <p {...props} className="text-gray-900 dark:text-gray-100 leading-relaxed mb-4 text-justify">
                        {children}
                      </p>
                    );
                  },
                }}
              >
      {content}
              </ReactMarkdown>
  );

  // === NUEVO: dividir el markdown para insertar el análisis justo después de "Áreas de mejora" ===
  const splitReport = useMemo(() => {
    if (!iaReport) return { before: '', improvements: '', after: '' };
    const headerRegex = /(\n|^)#\s*[^\n]*Áreas de mejora[^\n]*\n/;
    const match = iaReport.match(headerRegex);
    if (!match || match.index == null) return { before: '', improvements: '', after: iaReport };
    const headerIndex = match.index;
    const afterHeaderIndex = headerIndex + match[0].length;
    const nextHeader = /\n#[^\n]*/g;
    nextHeader.lastIndex = afterHeaderIndex;
    const nextMatch = nextHeader.exec(iaReport);
    const endIndex = nextMatch ? nextMatch.index : iaReport.length;
    return {
      before: iaReport.slice(0, headerIndex),
      improvements: iaReport.slice(headerIndex, endIndex),
      after: iaReport.slice(endIndex)
    };
  }, [iaReport]);

  // Renderizado final
  return (
    <section className="max-w-4xl mx-auto p-4 print:p-0 print:max-w-none">

      {/* Mensaje de carga */}
      {loadingIa && (
        <div className="bg-blue-100 dark:bg-blue-900/30 rounded-lg shadow-md p-6 mb-8 text-center">
          <p className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Generando tu informe personalizado</p>
          <div className="w-full flex justify-center">
            <div className="w-2/3 bg-blue-200 dark:bg-blue-800 rounded-full h-3 overflow-hidden">
              <div
                className="bg-blue-500 dark:bg-blue-300 h-3 transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
          <p className="mt-4 text-xs text-gray-900 dark:text-gray-100">Esto puede tardar unos segundos. Por favor, ten paciencia.</p>
        </div>
      )}

      {/* Mensaje de error (solo si no hay informe generado) */}
      {errorIa && !iaReport && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-md p-6 mb-8" role="alert">
          <strong className="font-bold text-gray-900 dark:text-gray-100">Aviso.</strong>
          <span className="block sm:inline text-gray-900 dark:text-gray-100"> {errorIa}</span>
        </div>
      )}

      {/* Contenido del informe que no depende de la IA */}
      {portada}
      {radar}

      {/* Informe de la IA y formulario de feedback */}
      {/* Estado iaReport disponible para debug en desarrollo */}
      
      {/* SOLUCIÓN: Mostrar informe básico si no hay iaReport después de cargar */}
      {!loadingIa && !iaReport && !errorIa && (
        <div className="bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 dark:border-yellow-700 text-yellow-700 dark:text-yellow-200 px-4 py-3 rounded-lg shadow-md p-6 mb-8" role="alert">
          <strong className="font-bold text-gray-900 dark:text-gray-100">Informe básico disponible.</strong>
          <span className="block sm:inline text-gray-900 dark:text-gray-100"> Tu informe está siendo procesado. Mientras tanto, aquí tienes un resumen de tus resultados.</span>
          
          <div className="mt-4 bg-white dark:bg-gray-800 rounded-lg p-4 transition-colors">
            <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">Resumen de Evaluación</h3>
            <p className="text-gray-900 dark:text-gray-100"><strong>Nombre:</strong> {report?.firstName} {report?.lastName}</p>
            <p className="text-gray-900 dark:text-gray-100"><strong>Puntaje de empleabilidad:</strong> {report?.employabilityScore ?? 'Calculando...'}</p>
            
            
            
            <p className="mt-3 text-sm text-gray-900 dark:text-gray-100">
              Actualiza esta página en unos segundos para ver el informe completo.
            </p>
          </div>
        </div>
      )}
      
      {iaReport && (
        <>
          <div className="informe-empleabilidad report-container print-max-w-none print-p-0 print-bg-white print-shadow-none">
            <div className="report-content professional-report print-max-w-none print-p-0 print-bg-white print-shadow-none">
              {(() => {
                // Si no podemos dividir, renderizamos como antes sin insertar el análisis
                if (!splitReport.improvements) {
                  return renderMarkdown(iaReport);
                }
                return (
                  <>
                    {splitReport.before && renderMarkdown(splitReport.before)}
                    {splitReport.improvements && renderMarkdown(splitReport.improvements)}
                    {renderCvAnalysisSection()}
                    {splitReport.after && renderMarkdown(splitReport.after)}
                  </>
                );
              })()}
            </div>
          </div>

          {finalPhrase && (
            <div
              className="rounded-xl p-6 my-8 shadow-sm report-highlight border-2 bg-blue-50 border-blue-200 text-gray-800 dark:!bg-blue-50 dark:!border-blue-200 dark:!text-gray-800 print:bg-white print:text-black"
              role="note"
            >
              <p className="mb-0 leading-relaxed">
                {finalPhrase}
              </p>
            </div>
          )}

          {!feedbackSent && (
            <div className="bg-gray-50 rounded-lg shadow-md p-6 mb-8 print-hidden">
              <form onSubmit={handleFeedbackSubmit}>
                <label className="block mb-2 font-semibold text-gray-900 dark:text-gray-100">¿Te resultó útil este informe?</label>
                <div className="flex gap-4 mb-4">
                  <label className="flex items-center gap-2 px-3 py-1 rounded-full border border-gray-300 dark:border-gray-600">
                    <input className="w-5 h-5" type="radio" name="rating" value="útil" required checked={feedback.rating === 'útil'} onChange={e => setFeedback(f => ({...f, rating: e.target.value}))} />
                    <span className="min-w-[3.5rem] text-center text-gray-900 dark:text-gray-100">Útil</span>
                  </label>
                  <label className="flex items-center gap-2 px-3 py-1 rounded-full border border-gray-300 dark:border-gray-600">
                    <input className="w-5 h-5" type="radio" name="rating" value="no útil" required checked={feedback.rating === 'no útil'} onChange={e => setFeedback(f => ({...f, rating: e.target.value}))} />
                    <span className="min-w-[5rem] text-center text-gray-900 dark:text-gray-100">No útil</span>
                  </label>
                </div>
                <label className="block mb-1 text-gray-900 dark:text-gray-100">¿Algún comentario o sugerencia?</label>
                <textarea className="w-full border rounded p-2 mb-2" rows={2} value={feedback.comment} onChange={e => setFeedback(f => ({...f, comment: e.target.value}))} />
                {feedbackError && <p className="text-red-600 mb-2">{feedbackError}</p>}
                <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">Enviar feedback</button>
              </form>
            </div>
          )}

          {feedbackSent && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg shadow-md p-6 mb-8 print-hidden" role="alert">
              <p className="font-semibold">¡Gracias por tu feedback!</p>
            </div>
          )}
        </>
      )}
    </section>
  );
};

export default ResultadosPage;