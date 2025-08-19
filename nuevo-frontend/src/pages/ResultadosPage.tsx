// src/pages/ResultadosPage.tsx
import React, { useEffect, useState, useRef } from 'react';
import { useAppSelector } from '../app/hooks';
import type { RootState } from '../app/store';
import { buildApiUrl, API_CONFIG } from '../config/api';
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
import { generateFinalReport } from '../features/personal/personalSlice';

// Definir tipos locales para evitar importaciones problemáticas


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
      const json = JSON.parse(match[1]);
      if (json && Array.isArray(json.radarData)) {
        return json.radarData;
      }
    } catch (e) {
      // Ignorar errores de parseo
    }
  }
  return [];
}

// Función helper para mapeo seguro


// Eliminada: helper no usado tras la remaquetación del informe

// Utilidades para limpiar duplicaciones de nombre en el resumen
function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function removeLeadingName(summary: string, candidate: string): string {
  if (!summary || !candidate) return summary;
  const pattern = new RegExp(`^${escapeRegExp(candidate)}[\\s,.:;-]*`, 'i');
  return summary.replace(pattern, '').trimStart();
}

// Convierte enumeraciones en línea ("1) ...; 2) ...") en listas Markdown accesibles
function formatListsForAccessibility(text: string): string {
  if (!text || typeof text !== 'string') return '';
  let s = text.trim();
  // Reemplazar patrones tipo "1) ", "2. " por "- " con salto de línea, manteniendo separadores previos
  s = s.replace(/(^|[\s;(])\d+[).]\s+/g, '$1\n- ');
  // Quitar ";" antes de saltos de línea de lista
  s = s.replace(/;\s*\n- /g, '\n- ');
  // Dejar un salto adicional tras ":" para separar párrafos y lista
  s = s.replace(/:\s*\n- /g, ':\n\n- ');
  // Eliminar puntuación terminal sobrante de cada item
  s = s.replace(/(- [^\n]+)[;.,]\s*$/gm, '$1');
  // Compactar saltos múltiples
  s = s.replace(/\n{3,}/g, '\n\n');
  return s;
}

// Genera estrellas de 1-5 para lectura fácil
function renderStars(score: number): string {
  const n = Math.max(0, Math.min(5, Math.round(score)));
  return '★'.repeat(n) + '☆'.repeat(5 - n);
}

// Sanea frases con sectores concretos no respaldados por el CV
function sanitizeProfileSummary(text: string, cvData: unknown): string {
  try {
    const summary = String(text || '');
    const haystack = JSON.stringify(cvData || {}).toLowerCase();
    // Reemplazar "experiencia en el sector de X" si X no aparece en el CV
    return summary.replace(/experiencia en el sector de ([^,.;\n]+)/gi, (_m, sector) => {
      const token = String(sector || '').trim().toLowerCase();
      if (!token) return 'experiencia relevante';
      return haystack.includes(token) ? _m : 'experiencia relevante';
    });
  } catch {
    return String(text || '');
  }
}

// Limpia frases como "Puntuación baja (35/100)" dejando solo la puntuación
function sanitizeImprovementText(text: string): string {
  try {
    let s = String(text || '').trim();
    // Mantener únicamente el valor numérico si viene como "Puntuación baja (35/100)"
    s = s.replace(/Puntuación\s+(?:muy\s+)?(?:baja|media|alta)\s*\((\d+\s*\/\s*\d+)\)/gi, '($1)');
    // O como "Puntuación baja: 35/100" o "Puntuación baja 35/100"
    s = s.replace(/Puntuación\s+(?:muy\s+)?(?:baja|media|alta)\s*:?\s*(\d+\s*\/\s*\d+)/gi, '$1');
    // Eliminar etiquetas de calificación si no tienen número detrás
    s = s.replace(/Puntuación\s+(?:muy\s+)?(?:baja|media|alta)/gi, '').replace(/\s{2,}/g, ' ').trim();
    // Quitar guiones directamente antes de la puntuación para que quede como en "Fortalezas"
    // Ej.: "Toma de decisiones - (35/100)" -> "Toma de decisiones (35/100)"
    s = s.replace(/\s*[-–—]\s*\((\d+\s*\/\s*\d+)\)/g, ' ($1)');
    // Y si viniera sin paréntesis: "- 35/100" -> " 35/100"
    s = s.replace(/\s*[-–—]\s*(\d+\s*\/\s*\d+)\b/g, ' $1');
    s = s.replace(/\s{2,}/g, ' ').trim();
    return s;
  } catch {
    return String(text || '');
  }
}

  // Heurísticas simples para evaluar un CV sin IA (formato, claridad, coherencia, información clave, ortografía)
type CvHeuristicInput = Partial<{
  strengths: string[];
  weaknesses: string[];
  skills: string[];
  education: string[];
  feedback: string;
    alerts: string[];
}> | null;

  function rateCv(cv: CvHeuristicInput): { formato: number; claridad: number; coherencia: number; infoClave: number; ortografia: number; razones: string[] } {
  if (!cv || typeof cv !== 'object') {
    return { formato: 3, claridad: 3, coherencia: 3, infoClave: 3, ortografia: 3, razones: ['No se encontraron datos del CV.'] };
  }
  const strengths = Array.isArray(cv.strengths) ? cv.strengths : [];
  const weaknesses = Array.isArray(cv.weaknesses) ? cv.weaknesses : [];
  const skills = Array.isArray(cv.skills) ? cv.skills : [];
  const education = Array.isArray(cv.education) ? cv.education : [];
  const feedback = typeof cv.feedback === 'string' ? cv.feedback : '';

  // Formato: presencia de secciones y longitud moderada del feedback
  const formato = (education.length > 0 && skills.length > 3 ? 4 : 3) + (feedback.length > 120 ? 1 : 0);

  // Claridad: cantidad de fortalezas y que el feedback exista
  const claridad = (strengths.length >= 3 ? 4 : 3) + (feedback.length > 80 ? 1 : 0);

  // Coherencia: si aparecen puntos de mejora y fortalezas equilibrados
  const coherencia = (weaknesses.length > 0 && strengths.length > 0) ? 4 : 3;

  // Información clave: número de skills y educación
  const infoClave = (skills.length >= 5 ? 4 : 3) + (education.length >= 1 ? 1 : 0);

  // Ortografía: heurística básica (dobles espacios, signos mal cerrados, exceso de mayúsculas)
    const doubleSpaces = /\s{2,}/.test(feedback);
    const longAllCaps = /\b[A-ZÁÉÍÓÚÜÑ]{6,}\b/.test(feedback);
    const punctuationIssues = /\s[,;:.]/.test(feedback);
    const spellingHint = Array.isArray(cv.alerts) && cv.alerts.join(' ').toLowerCase().includes('faltas de ortografía');
  let ortografiaBase = 4;
  if (doubleSpaces) ortografiaBase -= 1;
  if (longAllCaps) ortografiaBase -= 1;
  if (punctuationIssues) ortografiaBase -= 1;
    if (spellingHint) ortografiaBase -= 1;
  const ortografia = Math.max(2, Math.min(5, ortografiaBase));

  const razones: string[] = [];
  if (skills.length > 0) razones.push(`Incluye ${skills.length} habilidades identificadas.`);
  if (education.length > 0) razones.push(`Formación registrada (${education.length} entradas).`);
  if (strengths.length > 0) razones.push(`Fortalezas destacadas (${strengths.length}).`);
  if (weaknesses.length > 0) razones.push(`Áreas de mejora detectadas (${weaknesses.length}).`);
  if (doubleSpaces) razones.push('Se detectaron dobles espacios.');
  if (longAllCaps) razones.push('Uso excesivo de mayúsculas en palabras largas.');
    if (punctuationIssues) razones.push('Espacios antes de signos de puntuación.');
    if (spellingHint) razones.push('Se detectaron posibles faltas de ortografía.');

  return {
    formato: Math.max(1, Math.min(5, formato)),
    claridad: Math.max(1, Math.min(5, claridad)),
    coherencia: Math.max(1, Math.min(5, coherencia)),
    infoClave: Math.max(1, Math.min(5, infoClave)),
    ortografia,
    razones,
  };
}

const ResultadosPage: React.FC = () => {
  const dispatch = useDispatch();
  const personal = useAppSelector((state: RootState) => state.personal);
  const cvAnalysis = personal?.cvAnalysis;
  const report = personal?.report;
  const fecha = new Date().toLocaleDateString();
  const game = useAppSelector((state: RootState) => state.game);

  // Debug logging usando la utilidad (comentado para producción)
  // debugState(state, 'ResultadosPage');

  // Generar report si no existe
  useEffect(() => {
    if (!report && personal.softSkills && personal.softSkills.length > 0) {
      dispatch(generateFinalReport());
    }
  }, [report, personal.softSkills, dispatch]);

  // Estado para el informe IA
  const [iaReport, setIaReport] = useState<string>('');
  const [iaScore, setIaScore] = useState<number | undefined>(undefined);
  const [loadingIa, setLoadingIa] = useState<boolean>(false);
  const [errorIa, setErrorIa] = useState<string>('');
  const fetchedRef = useRef(false);
  const [finalPhrase, setFinalPhrase] = useState<string>('');

  // Llamar al endpoint de IA al cargar la página
  useEffect(() => {
    const fetchIaReport = async () => {
      setLoadingIa(true);
      setErrorIa('');
      
      try {
        // SOLUCIÓN: Asegurar que siempre hay datos mínimos para el informe
        const userFullName = `${report?.firstName || ''} ${report?.lastName || ''}`.trim() || 'Usuario';
        const validSoftSkills = filterValidSoftSkills(personal.softSkills || []);
        
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
          completedGames: game?.completedGames || [],
          logs: []
        };

        const res = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.IA_REPORT), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody),
          signal: AbortSignal.timeout(180000), // Timeout de 3 minutos
        });
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
        // Relajar condición: con que exista summary mostramos el informe; el resto es opcional
        if (res.ok && data && data.summary) {
          // Generar informe profesional con el nuevo formato
          try {
            const candidateName = String(data?.report?.fullName || userFullName);
            const cleanedSummary = formatListsForAccessibility(
              removeLeadingName(String(data.summary || ''), candidateName)
            );
            // Datos personales: preferir recomendaciones, luego report.ui y por último contact del CV
            const dpSrc = (data as { recommendations?: { datos_personales?: Record<string, unknown> }; report?: { ui?: { datos_personales?: Record<string, unknown> } } })?.recommendations?.datos_personales
              || (data as { report?: { ui?: { datos_personales?: Record<string, unknown> } } })?.report?.ui?.datos_personales
              || {} as Record<string, unknown>;
            const contact = (data as { report?: { cvAnalysis?: { contact?: { emails?: string[]; phones?: string[]; location?: string } } } })?.report?.cvAnalysis?.contact
              || (cvAnalysis as { contact?: { emails?: string[]; phones?: string[]; location?: string } } | null | undefined)?.contact
              || {} as { emails?: string[]; phones?: string[]; location?: string };
            const dp = {
              name: dpSrc?.name || candidateName,
              location: dpSrc?.location || contact?.location || 'No consta',
              email: dpSrc?.email || (Array.isArray(contact?.emails) ? contact.emails[0] : '') || 'No consta',
              phone: dpSrc?.phone || (Array.isArray(contact?.phones) ? contact.phones[0] : '') || 'No especificado',
              disability_certificate: (dpSrc?.disability_certificate != null)
                ? dpSrc.disability_certificate
                : ((report?.jobPreferences as any)?.hasDisabilityCert ? 'Sí' : 'No')
            };
            const profileSummaryRaw = (data as { recommendations?: { resumen_perfil?: string; analisis_perfil?: string } })?.recommendations?.resumen_perfil
              || (data as { recommendations?: { analisis_perfil?: string } })?.recommendations?.analisis_perfil
              || cleanedSummary;
            const profileSummary = sanitizeProfileSummary(
              profileSummaryRaw,
              (data as any)?.report?.cvAnalysis || cvAnalysis
            );
            const rec = ((data as { recommendations?: Record<string, unknown> })?.recommendations) || {} as Record<string, unknown>;

            const informe = `# Informe Profesional de Empleabilidad

## Datos personales básicos
- **Nombre**: ${dp.name || candidateName}
- **Ubicación**: ${dp.location || 'No consta'}
- **Email | Tel.**: ${(dp.email || 'No consta')} | ${(dp.phone || 'No consta')}
- **Certificado de discapacidad**: ${(String(dp.disability_certificate || '').toLowerCase().includes('sí') ? 'Sí' : 'No')}

## Resumen del perfil
${formatListsForAccessibility(String(profileSummary || 'Resumen no disponible.'))}

## Resumen del CV
${(() => {
  const txt = String(rec.resumen_cv || '');
  const cvx = (data?.report?.cvAnalysis || cvAnalysis || {}) as { cv_structured?: unknown };
  const structured = (cvx && (cvx.cv_structured || {})) as Record<string, unknown>;
  const hasStructured = structured && (Array.isArray(structured.experience) || Array.isArray(structured.education));
  // 1) Si hay datos estructurados, siempre los mostramos (con o sin texto adicional)
  if (hasStructured) {
    const fmtRange = (e: { start_date?: string; end_date?: string; current?: boolean }) => {
      const s = String(e?.start_date || '').trim();
      const end = (e?.current ? 'actualidad' : String(e?.end_date || '').trim());
      const both = [s, end].filter(Boolean).join(' – ');
      return both ? ` (${both})` : '';
    };
    const take = <T,>(arr: T[] | undefined, n = 4): T[] => Array.isArray(arr) ? arr.slice(0, n) : [];
    const expLines = take(structured.experience as Array<{ position?: string; title?: string; company?: string; organization?: string; organisation?: string; start_date?: string; end_date?: string; current?: boolean }>, 4).map((e) => {
      const role = String(e?.position || e?.title || 'Puesto').trim();
      const company = String(e?.company || e?.organization || e?.organisation || '').trim();
      const at = company ? ` en ${company}` : '';
      return `- ${role}${at}${fmtRange(e)}`;
    });
    const eduLines = take(structured.education as Array<{ degree?: string; title?: string; institution?: string; school?: string; start_date?: string; end_date?: string }>, 4).map((it) => {
      const degree = String(it?.degree || it?.title || 'Estudios').trim();
      const inst = String(it?.institution || it?.school || '').trim();
      const years = [it?.start_date, it?.end_date].filter(Boolean).join(' – ');
      const tail = [inst, years].filter(Boolean).join(', ');
      return `- ${degree}${tail ? ` — ${tail}` : ''}`;
    });
    const langLines = take(structured.languages as Array<{ language?: string; name?: string; level?: string }>, 5).map((l) => `- ${String(l?.language || l?.name || 'Idioma')} — ${String(l?.level || '').trim() || 'nivel no indicado'}`);
    const rawSkills = (structured.skills as Array<{ name?: string; tool?: string }> | undefined) ?? [];
    const altSoftware = (structured as { software?: Array<{ name?: string; tool?: string }> }).software ?? [];
    const skillsArr = (Array.isArray(rawSkills) && rawSkills.length > 0) ? rawSkills : altSoftware;
    const skillLines = take(skillsArr, 8).map((s) => `- ${String((s as { name?: string }).name || (s as { tool?: string }).tool || s || '')}`);

    const blocks: string[] = [];
    if (expLines.length) blocks.push(`### Experiencia destacada\n${expLines.join('\n')}`);
    if (eduLines.length) blocks.push(`### Formación\n${eduLines.join('\n')}`);
    if (langLines.length) blocks.push(`### Idiomas\n${langLines.join('\n')}`);
    if (skillLines.length) blocks.push(`### Herramientas/Software\n${skillLines.join('\n')}`);

    const header = `Se ha extraído información estructurada del CV:`;
    const textExtra = (txt && !/no hay información del cv/i.test(txt) && !/información.*limitad/i.test(txt))
      ? `\n\n${formatListsForAccessibility(txt)}`
      : '';
    return `${header}\n\n${blocks.join('\n\n')}${textExtra}`;
  }
  // 2) Si no hay estructurado, usar el texto si es útil
  if (txt && !/no hay información del cv/i.test(txt)) {
    return formatListsForAccessibility(txt);
  }
  return 'Resumen del CV no disponible.';
})()}

## Fortalezas
${(() => {
  const arr = Array.isArray(rec.fortalezas_clave) ? rec.fortalezas_clave : [];
  return arr.length > 0 ? arr.map((x: unknown) => `- ${String(x)}`).join('\n') : '- Información no disponible.';
})()}

## Áreas de mejora y consejos
${(() => {
  const arr = Array.isArray((rec as { areas_mejora?: unknown[] }).areas_mejora) ? (rec as { areas_mejora?: unknown[] }).areas_mejora as unknown[] : [];
  return arr.length > 0
    ? arr.map((x: unknown) => `- ${sanitizeImprovementText(String(x))}`).join('\n')
    : '- Información no disponible.';
})()}

## Análisis del CV (con puntuación 1–5 por apartado)
${(() => {
  // Preferir el diagnóstico del backend si existe; si no, usar heurística local
  try {
    const dx: any = (rec && (rec as any).diagnostico_cv) || {};
    const hasBackendScores = [dx.structure_score, dx.coherence_score, dx.key_info_score, dx.clarity_score, (dx.spelling_style_score ?? dx.style_score)]
      .some((v: any) => typeof v === 'number' && v > 0);
    if (hasBackendScores) {
      const stars = [
        `Formato: ${renderStars(Number(dx.structure_score || 1))}`,
        `Claridad: ${renderStars(Number(dx.clarity_score || 1))}`,
        `Coherencia: ${renderStars(Number(dx.coherence_score || 1))}`,
        `Información clave: ${renderStars(Number(dx.key_info_score || 1))}`,
        `Ortografía y estilo: ${renderStars(Number((dx.spelling_style_score ?? dx.style_score) || 1))}`,
      ].join('  \\\n');
      const ev: any = (dx && dx.evidence) || {};
      const evLines: string[] = [];
      const pushIfUseful = (label: string, value: unknown) => {
        const s = typeof value === 'string' ? value.trim() : '';
        if (!s) return;
        if (/no hay información del cv/i.test(s)) return; // descartar textos genéricos
        evLines.push(`- ${label}: ${s}`);
      };
      pushIfUseful('Estructura', ev.structure);
      pushIfUseful('Claridad', ev.clarity);
      pushIfUseful('Coherencia', ev.coherence);
      pushIfUseful('Información clave', ev.key_info);
      pushIfUseful('Ortografía y estilo', ev.style);
      const corr = Array.isArray(dx.corrections) && dx.corrections.length > 0
        ? [`\nCorrecciones/Acciones:`, ...dx.corrections.map((c: any) => `- ${String(c)}`)]
        : [];
      const reord = Array.isArray(dx.reordering_suggestions) && dx.reordering_suggestions.length > 0
        ? [`\nReordenación sugerida:`, ...dx.reordering_suggestions.map((r: any) => `- ${String(r)}`)]
        : [];

      // Si no quedan evidencias útiles, usar heurística local con cvAnalysis
      if (evLines.length === 0) {
        const cvLocal = data?.report?.cvAnalysis || cvAnalysis || null;
        const rLoc = rateCv(cvLocal);
        const starsHeur = [
          `Formato: ${renderStars(rLoc.formato)}`,
          `Claridad: ${renderStars(rLoc.claridad)}`,
          `Coherencia: ${renderStars(rLoc.coherencia)}`,
          `Información clave: ${renderStars(rLoc.infoClave)}`,
          `Ortografía: ${renderStars(rLoc.ortografia)}`,
        ].join('  \\\n');
        const razones = Array.isArray(rLoc.razones) && rLoc.razones.length > 0 ? `\n\n${rLoc.razones.map(x => `- ${x}`).join('\n')}` : '';
        const extras = (corr.length || reord.length) ? `\n\n${[...corr, ...reord].join('\n')}` : '';
        return `${starsHeur}${razones}${extras}`;
      }

      const razonesBlock = `\n\n${[...evLines, ...corr, ...reord].join('\n')}`;
      return `${stars}${razonesBlock}`;
    }
  } catch (e) {
    // Silenciar errores no críticos en el renderizado del markdown del diagnóstico
  }
  // Fallback heurístico
  const cv = data?.report?.cvAnalysis || cvAnalysis || null;
  const r = rateCv(cv);
  const stars = [
    `Formato: ${renderStars(r.formato)}`,
    `Claridad: ${renderStars(r.claridad)}`,
    `Coherencia: ${renderStars(r.coherencia)}`,
    `Información clave: ${renderStars(r.infoClave)}`,
    `Ortografía: ${renderStars(r.ortografia)}`,
  ].join('  \\\n');
  const razones = Array.isArray(r.razones) && r.razones.length > 0 ? `\n\n${r.razones.map(x => `- ${x}`).join('\n')}` : '';
  return `${stars}${razones}`;
})()}
## Entornos de trabajo ideales
${formatListsForAccessibility(String(rec.entornos_ideales || 'Información no disponible.'))}

## Roles profesionales sugeridos
${(() => {
  const arr = Array.isArray(rec.roles_sugeridos) ? rec.roles_sugeridos : [];
  return arr.length > 0 ? arr.map((x: unknown) => `- ${String(x)}`).join('\n') : '- Información no disponible.';
})()}

## Plan de acción
### Corto plazo (0–30 días)
${(() => { const steps = (rec as { plan_accion?: { corto_plazo?: unknown[] } })?.plan_accion?.corto_plazo || []; return Array.isArray(steps) && steps.length > 0 ? steps.map((s: unknown) => `- ${String(s)}`).join('\n') : '- Actualizar CV\n- Crear perfil en LinkedIn'; })()}

### Medio plazo (1–3 meses)
${(() => { const steps = (rec as { plan_accion?: { medio_plazo?: unknown[] } })?.plan_accion?.medio_plazo || []; return Array.isArray(steps) && steps.length > 0 ? steps.map((s: unknown) => `- ${String(s)}`).join('\n') : '- Completar formación específica\n- Ampliar red profesional'; })()}

### Largo plazo (3–6+ meses)
${(() => { const steps = (rec as { plan_accion?: { largo_plazo?: unknown[] } })?.plan_accion?.largo_plazo || []; return Array.isArray(steps) && steps.length > 0 ? steps.map((s: unknown) => `- ${String(s)}`).join('\n') : '- Desarrollar especialización\n- Buscar oportunidades de liderazgo'; })()}

## Consejos de búsqueda de empleo
${(() => {
  try {
    const adv: any = rec.consejos_busqueda || {};
    const secciones: string[] = [];
    const cvOpt = Array.isArray(adv.cv_optimization) ? adv.cv_optimization : [];
    if (cvOpt.length > 0) secciones.push(`### Optimización del CV\n${cvOpt.map((x: unknown) => `- ${String(x)}`).join('\n')}`);
    if (adv.letters_portfolio) secciones.push(`### Cartas y portfolio/casos\n${String(adv.letters_portfolio)}`);
    const plats = Array.isArray(adv.recommended_platforms) ? adv.recommended_platforms : [];
    if (plats.length > 0) secciones.push(`### Plataformas\n${plats.map((x: unknown) => `- ${String(x)}`).join('\n')}`);
    if (adv.networking) secciones.push(`### Networking dirigido\n${String(adv.networking)}`);
    if (adv.interview_tips) secciones.push(`### Entrevistas (método STAR)\n${String(adv.interview_tips)}`);
    return secciones.length > 0 ? secciones.join('\n\n') : 'Consejos no disponibles.';
  } catch {
    return 'Consejos no disponibles.';
  }
})()}

## Herramientas útiles y tecnología
${(() => {
  const tools: any = rec.herramientas_utiles || {};
  const renderCat = (title: string, items: any[]) => {
    if (!Array.isArray(items) || items.length === 0) return '';
    return `### ${title}\n${items.map((it: any) => {
      if (it && typeof it === 'object') {
        const title = String(it.name || it.title || 'Recurso');
        const desc = it.description ? `\n${String(it.description)}` : '';
        const link = it.url ? `\n[${title}](${it.url})` : '';
        return `- ${title}${desc}${link}`;
      }
      return `- ${String(it)}`;
    }).join('\n')}`;
  };
  const parts = [
    renderCat('Productividad/organización', tools.productividad || []),
    renderCat('Búsqueda de empleo y alertas', tools.busqueda || []),
    renderCat('Aprendizaje/certificación', tools.aprendizaje || []),
    renderCat('Accesibilidad/neuroinclusión', tools.accesibilidad || []),
  ].filter(Boolean);
  return parts.length > 0 ? parts.join('\n\n') : 'Sin recomendaciones específicas. Prueba con LinkedIn Learning, InfoJobs y Platzi.';
})()}

---
*Informe profesional generado el ${data.createdAt ? new Date(data.createdAt).toLocaleDateString('es-ES') : new Date().toLocaleDateString('es-ES')}*`;
            if (import.meta.env.MODE !== 'production') {
              // eslint-disable-next-line no-console
              console.log('✅ DEBUG - Informe generado exitosamente. Longitud:', informe.length);
              // eslint-disable-next-line no-console
              console.log('✅ DEBUG - Primeros 200 caracteres:', informe.substring(0, 200));
            }
            setIaReport(informe);
            // Frase motivacional final destacada (fuera del markdown principal)
            const frase = String(rec.frase_final || '').trim();
            const prefix = 'Este informe ha sido elaborado en base a tus preferencias laborales, los resultados de los minijuegos y tu CV. ';
            const composed = (frase && !frase.toLowerCase().startsWith('este informe')) ? prefix + frase : (frase || prefix + 'Aprovecha tus fortalezas y confía en tu potencial. ¡Mucha suerte!');
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
            console.log('  - data.summary:', !!data?.summary);
            // eslint-disable-next-line no-console
            console.log('  - data.recommendations:', !!data?.recommendations);
          }
          setErrorIa('No se pudo generar el informe IA.');
        }
      } catch (err) {
        // console.error('Error en fetchIaReport:', err);
        if (err instanceof Error && err.name === 'TimeoutError') {
          setErrorIa('El informe está tardando más de lo esperado. Se generará un informe básico automáticamente.');
        } else if (err instanceof Error && err.message?.includes('Failed to fetch')) {
          setErrorIa('No se pudo conectar con el servidor. Verifica tu conexión a internet.');
        } else {
          // Si hay otros errores pero el informe se generó, no mostrar error
          // Advertencia en generación de informe
          // No establecer errorIa para que no se muestre el mensaje de error
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
      <h1 className="text-4xl font-bold mb-2">Informe de Empleabilidad</h1>
      <h2 className="text-2xl font-semibold mb-1">{report?.firstName} {report?.lastName}</h2>
      <p className="text-gray-600 dark:text-gray-300">{fecha}</p>
      
      {/* Botones de acción */}
      <div className="flex gap-4 mt-6 print-hidden">
        <button
          onClick={handlePrint}
          disabled={!iaReport}
          className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
            !iaReport
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
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
    return data
      .map(item => ({
        softskill: item.skill || item.softskill || '',
        score: Number(item.score) || 0,
      }))
      .filter(item => {
        if (seen.has(item.softskill)) {
          return false; // Eliminar duplicados
        }
        seen.add(item.softskill);
        return item.score > 0; // Solo elementos con score válido
      });
  };

  const mergedSoftSkills = useMemo(() => filterValidSoftSkills(personal.softSkills || []), [personal.softSkills]);
  const computedScore = useMemo(() => {
    if (!mergedSoftSkills || mergedSoftSkills.length === 0) return undefined;
    const sum = mergedSoftSkills.reduce((acc, s) => acc + (Number(s.score) || 0), 0);
    return Math.round(sum / mergedSoftSkills.length);
  }, [mergedSoftSkills]);
  const globalScore = iaScore ?? report?.employabilityScore ?? computedScore;
  const radarData = radarDataFromIa.length > 0
    ? processRadarData(radarDataFromIa)
    : processRadarData(mergedSoftSkills);
  // Color de etiquetas del radar según modo (claro/oscuro)
  // Unificar color de etiquetas del radar: mismo tono que modo claro (fondo blanco en ambos)
  const isDarkMode = document.documentElement.classList.contains('dark');
  const radarLabelColor = isDarkMode ? '#F3F4F6' : '#0B1220';

  const radar = (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 mb-8 print-report-section print-page-break-inside-avoid transition-colors">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-gray-100">Mapa de habilidades</h2>
      <div className="flex flex-col md:flex-row gap-8 items-center">
        <div className="w-full md:w-1/2 h-96">
          {radarData.length > 0 ? (
            <ResponsiveRadar
              data={radarData}
              keys={["score"]}
              indexBy="softskill"
              margin={{ top: 40, right: 80, bottom: 40, left: 80 }}
              theme={{
                text: { fill: radarLabelColor, fontSize: 12 },
                grid: { line: { stroke: '#6B7280', strokeWidth: 1 } },
                axis: {
                  ticks: { text: { fill: radarLabelColor } },
                  domain: { line: { stroke: '#9CA3AF' } },
                  legend: { text: { fill: radarLabelColor } },
                },
                crosshair: { line: { stroke: '#F3F4F6' } },
              }}
              borderColor="#3B82F6"
              gridLabelOffset={20}
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
            <div className="flex items-center justify-center h-full text-gray-500">
              <p>No hay datos suficientes para mostrar el gráfico de habilidades</p>
            </div>
          )}
        </div>
        <div className="w-full md:w-1/2">
          <h3 className="font-semibold mb-2">Resumen de niveles:</h3>
          <ul className="space-y-1">
            {(() => {
              try {
                const validSkills = filterValidSoftSkills(personal.softSkills || []);
                return validSkills.map((skill, idx: number) => (
                  <li key={idx}>
                    <span className="font-medium">{skill.skill}:</span> {skill.score}%
                  </li>
                ));
              } catch (e) {
                return <li key="error">Error al cargar habilidades</li>;
              }
            })()}
          </ul>
          <p className="font-semibold mt-2">
            Puntaje global de empleabilidad: {globalScore ?? report?.employabilityScore ?? '-'}
          </p>
        </div>
      </div>
    </div>
  );

  // Ya no se necesitan las secciones hardcodeadas
  // El contenido ahora viene de la IA

  // Renderizado final
  return (
    <section className="max-w-4xl mx-auto p-4 print:p-0 print:max-w-none">

      {/* Mensaje de carga */}
      {loadingIa && (
        <div className="bg-blue-100 dark:bg-blue-900/30 rounded-lg shadow-md p-6 mb-8 text-center">
          <p className="text-lg font-semibold mb-4 dark:text-blue-100">Generando tu informe personalizado</p>
          <div className="w-full flex justify-center">
            <div className="w-2/3 bg-blue-200 dark:bg-blue-800 rounded-full h-3 overflow-hidden">
              <div
                className="bg-blue-500 dark:bg-blue-300 h-3 transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
          <p className="mt-4 text-xs text-gray-500 dark:text-gray-300">Esto puede tardar unos segundos. Por favor, ten paciencia.</p>
        </div>
      )}

      {/* Mensaje de error */}
      {errorIa && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-md p-6 mb-8" role="alert">
          <strong className="font-bold">Error de conexión.</strong>
          <span className="block sm:inline"> No se pudo generar el informe en este momento. Por favor, inténtalo de nuevo más tarde.</span>
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
          <strong className="font-bold">Informe básico disponible.</strong>
          <span className="block sm:inline"> Tu informe está siendo procesado. Mientras tanto, aquí tienes un resumen de tus resultados.</span>
          
          <div className="mt-4 bg-white dark:bg-gray-800 rounded-lg p-4 transition-colors">
            <h3 className="text-lg font-semibold mb-2">Resumen de Evaluación</h3>
            <p><strong>Nombre:</strong> {report?.firstName} {report?.lastName}</p>
            <p><strong>Puntaje de empleabilidad:</strong> {report?.employabilityScore ?? 'Calculando...'}</p>
            
            
            
            <p className="mt-3 text-sm text-gray-600">
              Actualiza esta página en unos segundos para ver el informe completo.
            </p>
          </div>
        </div>
      )}
      
      {iaReport && (
        <>
          <div className="informe-empleabilidad report-container print-max-w-none print-p-0 print-bg-white print-shadow-none">
            <div className="report-content professional-report print-max-w-none print-p-0 print-bg-white print-shadow-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  // Configuración mejorada para renderizado profesional
                  h1: ({ children, ...props }) => (
                    <h1 {...props} className="text-3xl font-bold text-gray-900 mb-6 mt-8 pb-2 border-b-2 border-gray-200 dark:border-gray-700">
                      {children}
                    </h1>
                  ),
                  h2: ({ children, ...props }) => (
                    <h2 {...props} className="text-2xl font-semibold text-gray-800 mb-4 mt-6">
                      {children}
                    </h2>
                  ),
                  h3: ({ children, ...props }) => (
                    <h3 {...props} className="text-xl font-semibold text-gray-700 mb-3 mt-5">
                      {children}
                    </h3>
                  ),
                  h4: ({ children, ...props }) => (
                    <h4 {...props} className="text-lg font-semibold text-gray-600 mb-2 mt-4">
                      {children}
                    </h4>
                  ),

                  ul: ({ children, ...props }) => (
                    <ul {...props} className="list-disc list-inside space-y-2 mb-4 text-gray-700">
                      {children}
                    </ul>
                  ),
                  ol: ({ children, ...props }) => (
                    <ol {...props} className="list-decimal list-inside space-y-2 mb-4 text-gray-700">
                      {children}
                    </ol>
                  ),
                  li: ({ children, ...props }) => (
                    <li {...props} className="leading-relaxed">
                      {children}
                    </li>
                  ),
                  strong: ({ children, ...props }) => (
                    <strong {...props} className="font-semibold text-gray-900">
                      {children}
                    </strong>
                  ),
                  em: ({ children, ...props }) => (
                    <em {...props} className="italic text-gray-600">
                      {children}
                    </em>
                  ),
                  blockquote: ({ children, ...props }) => (
                    <blockquote {...props} className="border-l-4 border-blue-500 pl-4 italic text-gray-600 bg-blue-50 dark:bg-blue-900/30 py-2 rounded-r">
                      {children}
                    </blockquote>
                  ),
                  code: ({ children, ...props }) => (
                      <code {...props} className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-sm font-mono text-gray-800">
                      {children}
                    </code>
                  ),
                  pre: ({ children, ...props }) => (
                    <pre {...props} className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg overflow-x-auto text-sm font-mono text-gray-800 border border-gray-200 dark:border-gray-600">
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
                    <th {...props} className="border border-gray-300 dark:border-gray-600 px-4 py-2 bg-gray-50 dark:bg-gray-800 font-semibold text-gray-900 text-left">
                      {children}
                    </th>
                  ),
                  td: ({ children, ...props }) => (
                    <td {...props} className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-700">
                      {children}
                    </td>
                  ),
                  a: ({ children, href, ...props }) => (
                    <a {...props} href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 underline">
                      {children}
                    </a>
                  ),
                  hr: ({ ...props }) => (
                    <hr {...props} className="border-t border-gray-300 my-6" />
                  ),
                                    // Componente personalizado para renderizar texto con estrellas coloreadas
                  p: ({ children, ...props }) => {
                    // Utilidad para extraer texto plano desde nodos React
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
                      // Verificar si es una línea de indicadores de calidad
                      if (/(Formato|Claridad|Coherencia|Información clave|Ortografía(?: y estilo)?):\s*[★☆]/.test(text)) {
                        // Extraer pares etiqueta + estrellas y mostrarlos en columna
                        const indicators: Array<{ label: string; stars: string }> = [];
                        const re = /(Formato|Claridad|Coherencia|Información clave|Ortografía(?: y estilo)?):\s*([★☆]+)/g;
                        let m: RegExpExecArray | null;
                        // eslint-disable-next-line no-cond-assign
                        while ((m = re.exec(text)) !== null) {
                          const rawLabel = m[1];
                          const normLabel = rawLabel.startsWith('Ortografía') ? 'Ortografía' : rawLabel;
                          indicators.push({ label: normLabel, stars: m[2] });
                        }
                        return (
                          <div {...props} className="quality-indicators">
                            <ul className="text-gray-700 leading-relaxed space-y-1">
                              {indicators.length > 0 ? indicators.map((it, idx) => {
                                const starMatch = it.stars.match(/(★+)(☆*)/);
                                const filledStars = starMatch ? starMatch[1] : '';
                                const emptyStars = starMatch ? starMatch[2] : '';
                                return (
                                  <li key={idx} className="flex items-center gap-2">
                                    <span className="font-semibold">{it.label}:</span>
                                    <span>
                                      <span className="star-filled">{filledStars}</span>
                                      <span className="star-empty">{emptyStars}</span>
                                    </span>
                                  </li>
                                );
                              }) : (
                                <li className="text-gray-700">{text}</li>
                              )}
                            </ul>
                          </div>
                        );
                      } else {
                        // Para otras estrellas en el texto, usar el renderizado normal
                        const parts = text.split(/((?:★+)(?:☆*))/g);
                        
                                                 return (
                           <p {...props} className="text-gray-700 leading-relaxed mb-4 text-justify">
                             {parts.map((part, index) => {
                               const starMatch = part.match(/(★+)(☆*)/);
                               if (starMatch) {
                                 const [, filledStars, emptyStars] = starMatch;
                                 const filledCount = filledStars.length;
                                 const totalCount = filledCount + emptyStars.length;
                                 const percentage = (filledCount / totalCount) * 100;
                                 
                                 let colorClass = 'star-very-poor'; // Por defecto
                                 if (percentage >= 90) colorClass = 'star-excellent'; // Verde esmeralda para excepcional
                                 else if (percentage >= 80) colorClass = 'star-very-good'; // Verde para excelente
                                 else if (percentage >= 70) colorClass = 'star-good'; // Verde lima para muy bueno
                                 else if (percentage >= 60) colorClass = 'star-average'; // Amarillo para bueno
                                 else if (percentage >= 50) colorClass = 'star-regular'; // Naranja para regular
                                 else if (percentage >= 40) colorClass = 'star-below-average'; // Naranja para regular-bajo
                                 else if (percentage >= 30) colorClass = 'star-poor'; // Rojo claro para bajo
                                 else colorClass = 'star-very-poor'; // Rojo para muy bajo
                                 
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
                               return part;
                             })}
                           </p>
                         );
                      }
                    }
                    return (
                      <p {...props} className="text-gray-700 leading-relaxed mb-4 text-justify">
                        {children}
                      </p>
                    );
                  },
                }}
              >
                {iaReport}
              </ReactMarkdown>
            </div>
          </div>

          {finalPhrase && (
            <div className="bg-blue-50 border-2 border-blue-200 text-gray-800 rounded-xl p-6 my-8 shadow-sm report-highlight" role="note">
              <p className="mb-0">
                {finalPhrase}
              </p>
            </div>
          )}

          {!feedbackSent && (
            <div className="bg-gray-50 rounded-lg shadow-md p-6 mb-8 print-hidden">
              <form onSubmit={handleFeedbackSubmit}>
                <label className="block mb-2 font-semibold">¿Te resultó útil este informe?</label>
                <div className="flex gap-4 mb-4">
                  <label className="flex items-center gap-2 px-3 py-1 rounded-full border border-gray-300 dark:border-gray-600">
                    <input className="w-5 h-5" type="radio" name="rating" value="útil" required checked={feedback.rating === 'útil'} onChange={e => setFeedback(f => ({...f, rating: e.target.value}))} />
                    <span className="min-w-[3.5rem] text-center">Útil</span>
                  </label>
                  <label className="flex items-center gap-2 px-3 py-1 rounded-full border border-gray-300 dark:border-gray-600">
                    <input className="w-5 h-5" type="radio" name="rating" value="no útil" required checked={feedback.rating === 'no útil'} onChange={e => setFeedback(f => ({...f, rating: e.target.value}))} />
                    <span className="min-w-[5rem] text-center">No útil</span>
                  </label>
                </div>
                <label className="block mb-1">¿Algún comentario o sugerencia?</label>
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