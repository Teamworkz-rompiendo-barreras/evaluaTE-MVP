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





// Helper para renderizar estrellas del CV de manera simplificada
const stars = (n?: number) => {
  const v = Math.max(0, Math.min(5, n ?? 0));
  return '★'.repeat(v) + '☆'.repeat(5 - v);
};



// Componente para renderizar estrellas (sin regex/escapes que rompan el lint)
const Stars: React.FC<{ n: CvStars }> = ({ n }) => (
  <span aria-label={`${n} de 5`}>{"★".repeat(n)}{"☆".repeat(5-n)}</span>
);

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

  const softSkills = Array.isArray(r?.soft_skills) ? r.soft_skills : [];
  const cv = r?.cv_analysis ?? {};
  const cvExp = Array.isArray(cv?.experience) ? cv.experience : [];
  const cvEdu = Array.isArray(cv?.education) ? cv.education : [];
  const cvLang = Array.isArray(cv?.languages) ? cv.languages : [];
  const cvSoft = Array.isArray(cv?.software) ? cv.software : [];

  const improvement = Array.isArray(r?.improvement_areas) ? r.improvement_areas : [];
  const environments = Array.isArray(r?.environments) ? r.environments : [];
  const roles = Array.isArray(r?.suggested_roles) ? r.suggested_roles : [];
  const plan = r?.action_plan ?? {};
  const tips = (r?.job_search_advice?.tips ?? r?.consejos_busqueda ?? []) as string[];
  const tools = r?.tools ?? {};
  const completed = Array.isArray(r?.completed_games) ? r.completed_games : [];
  const closing = r?.frase_final || '';

  // Utilidades
  const ssTop = [...softSkills].sort((a:any,b:any)=> (b?.score??0) - (a?.score??0));
  const top = ssTop[0] ? `${ssTop[0].skill} (${ssTop[0].score}/100)` : 'competencias clave';
  const secondary = ssTop.slice(1,4).map((s:any)=> s.skill).join(', ') || 'habilidades complementarias';

  const bullets = (arr: any[], formatter: (x:any)=>string) =>
    arr.length ? arr.map(formatter).map(s=>`* ${s}`).join('\n') : '* (no especificado)';

  const expBullets = bullets(cvExp, (e:any) =>
    `**${e.title || e.text || 'Experiencia'}${e.company ? `, ${e.company}` : ''}**${e.dates ? ` (${e.dates})` : ''}: ${e.summary || e.text || ''}`
  );

  const eduBullets = bullets(cvEdu, (e:any) =>
    `${e.degree || e.text || 'Formación'}${e.center ? ` – ${e.center}` : ''}${e.year ? ` (${e.year})` : ''}`
  );

  const langs = cvLang.length ? cvLang.map((l:any)=> l.text || l.name || l).join(', ') : 'no especificado';
  const softw = cvSoft.length ? cvSoft.join(', ') : 'Microsoft Office; Google Workspace';

  const fortalezas = softSkills.length
    ? softSkills.map((s:any)=> `* **${s.skill}** (${s.score || 0}/100)`).join('\n')
    : '* (pendiente de evaluación)';

  const areasMejora = improvement.length
    ? improvement.map((a:any, i:number)=> `${i+1}. **${a.area || a.name}**${a.score ? ` (${a.score}/100)` : ''}${a.reason ? `: ${a.reason}` : ''}`).join('\n')
    : '1. **Toma de decisiones** (35/100): definir criterios y checklists.\n2. **Influencia social** (35/100): preparar pitch corto con prueba de valor.';

  const diagRapido = [
    '**Logros cuantificados**: añade cifras y métricas específicas.',
    `**Palabras clave** para ATS: ${(r?.job_search_advice?.ats_keywords ?? []).join(', ') || 'data entry, data quality, OCR, Excel, QA'}.`,
    '**Estructura**: prioriza la experiencia más relevante.',
    '**LinkedIn**: crear/optimizar y enlazar en el CV.'
  ].map(s=>`* ${s}`).join('\n');

  const entornoBullets = bullets(environments, (e:any)=> e);

  const rolesBullets = roles.length
    ? roles.map((role:any) => `* **${role.role}** — *${role.seniority || 'Junior'}* — **${role.remote_viable ? '100% remoto' : 'Remoto viable'}**.\n\n  *Razón:* ${role.reason || 'alineación competencial'}`).join('\n')
    : '* **Data Entry / Back-office** — *Junior–Mid* — **100% remoto**.\n\n  *Razón:* experiencia directa en captura/transcripción y foco en precisión.';

  const plan030 = Array.isArray(plan.short_term) ? plan.short_term.map((x:string)=>`* ${x}`).join('\n')
    : '* Reescribir CV con métricas; crear LinkedIn.\n* Portafolio ligero con 2–3 pruebas de valor.\n* Acreditar tecleo e inglés funcional.';
  const plan60  = Array.isArray(plan.medium_term) ? plan.medium_term.map((x:string)=>`* ${x}`).join('\n')
    : '* 10–15 candidaturas/semana y 3 mensajes a reclutadores.\n* Aprender OCR/Airtable/Notion.\n* SOPs personales y checklist de calidad.';
  const plan90  = Array.isArray(plan.long_term) ? plan.long_term.map((x:string)=>`* ${x}`).join('\n')
    : '* 2–3 clientes/proyectos activos o 1 contrato estable.\n* Automatización ligera (macros/fórmulas).\n* Documentar KPIs (precisión, TAT).';

  const tipsBullets = tips.length ? tips.map(t=>`* ${t}`).join('\n')
    : '* Filtrar por **"remoto/teletrabajo"** y keywords relevantes.\n* Preparar **mensaje corto** para candidaturas.\n* Mantener un **registro** y hacer seguimientos.';

  const toolsSec = [
    `* **${(tools.productivity||['Excel','Google Sheets','Notion/Airtable']).join(', ')}**`,
    `* **${(tools.job_search||['LinkedIn','Indeed']).join(', ')}**`,
    `* **${(tools.learning||['Coursera','Udemy']).join(', ')}**`
  ].join('\n');

  const juegos = completed.length
    ? completed.map((g:any)=> `* **${g}**: capitaliza la competencia en tus entregables.`).join('\n')
    : '* **Liderazgo / Pensamiento analítico / Creatividad / Resiliencia**: refleja estas competencias con ejemplos y métricas.';

  const miniplan = [
    '**Decisiones:** usa una matriz rápida (Impacto × Esfuerzo) y límites de tiempo (10 min).',
    '**Influencia:** prepara un **pitch** de 3 líneas + 1 prueba de valor (antes/después).'
  ].map(s=>`* ${s}`).join('\n');

  const frasesListas = [
    '**Titular:** *Data Entry | QA de Datos | Back-office (100% remoto)*',
    '**Acerca de (3 líneas):**',
    '"Capturo y depuro datos con precisión y tiempos de entrega fiables. Experiencia en proyectos internacionales (Excel/Sheets, OCR, QA). Busco aportar orden y métricas claras a equipos remotos de operaciones y contenido."',
    '**Mensaje corto a reclutador/cliente:**',
    `"Hola, soy ${fullName.split(' ')[0] || '…'}. He realizado data entry y transcripción para clientes internacionales, con foco en precisión y SLA. Puedo enviar una muestra (hoja con limpieza + checklist de QA) y empezar de inmediato."`
  ].join('\n');

  const mensajeFinal = closing || `${fullName}, tienes una base excelente para **datos y operaciones remotas**. Con un CV cuantificado, un LinkedIn claro y 2–3 pruebas de valor, puedes convertir tu experiencia en **contratos estables** en 8–12 semanas.`;

  // === Markdown EXACTO ===
  return [
`# Resumen ejecutivo

Perfil con alta **${top}** y base sólida en **${secondary}**. Preferencia por **trabajo remoto** (si aplica), disponibilidad **completa** y apertura a **relocalización** (si aplica). ${cv?.summary ? cv.summary : 'Experiencia relevante en operaciones y gestión de datos.'} Áreas a potenciar: **${improvement.slice(0,2).map((a:any)=>a.area || a.name).join(' e ') || 'toma de decisiones e influencia social'}**.`,

`# Datos personales

* **Nombre:** ${fullName}
* **Ubicación:** ${location}
* **Email:** ${email}
* **Teléfono:** ${phone}
* **LinkedIn:** ${linkedin}`,

`# Resumen del CV

* **Experiencia (selección)**
${expBullets}

* **Formación** (selección)
${eduBullets}

* **Idiomas:** ${langs}
* **Software:** ${softw}`,

`# Fortalezas clave
${fortalezas}`,

`# Áreas de mejora priorizadas
${areasMejora}`,

`# Diagnóstico del CV (mejoras rápidas)
${diagRapido}`,

`# Entornos de trabajo ideales
${entornoBullets}`,

`# Roles sugeridos
${rolesBullets}`,

`# Plan de acción (30–60–90 días)

**0–30 días (bases)**
${plan030}

**31–60 días (tracción)**
${plan60}

**61–90 días (consolidación)**
${plan90}`,

`# Consejos prácticos de búsqueda
${tipsBullets}`,

`# Herramientas útiles
${toolsSec}`,

`# Juegos completados y cómo capitalizarlos
${juegos}`,

`# Miniplan para mejorar "toma de decisiones" e "influencia social"
${miniplan}`,

`# Frases listas (para propuestas y LinkedIn)
${frasesListas}`,

`# Mensaje final

${mensajeFinal}`
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
  const [cvStarsLocal, setCvStarsLocal] = useState<CvDiagnostico | null>(null);
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
    const fetchIaReport = async () => {
      setLoadingIa(true);
      setErrorIa('');
      
      // DEBUG: Agregar logs para entender el estado
      console.log('🔍 DEBUG - Estado personal completo:', personal);
      console.log('🔍 DEBUG - cvAnalysis del estado:', personal?.cvAnalysis);
      console.log('🔍 DEBUG - cvFile del estado:', personal?.cvFile);
      console.log('🔍 DEBUG - report del estado:', personal?.report);
      
      // Esperar a tener el análisis del CV si ya hay un archivo cargado
      // Evita lanzar el informe sin datos del CV recién subido
      if (personal?.cvFile && !personal?.cvAnalysis) {
        console.log('🔍 DEBUG - Hay CV pero no análisis, esperando...');
        setLoadingIa(false);
        return;
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

        // DEBUG: Log del requestBody completo
        console.log('🔍 DEBUG - requestBody completo:', requestBody);
        console.log('🔍 DEBUG - cvAnalysis en requestBody:', requestBody.cvAnalysis);

        const res = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.IA_REPORT), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody),
          signal: AbortSignal.timeout(180000), // Timeout de 3 minutos
        });
        
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
          // === NUEVO: inyectar radarData si el markdown no lo trae ===
          const hasRadar = /```json[\s\S]*"radarData"\s*:/.test(mdDeterministic);
          const radarJson = { radarData: (softSkillsToSend || []).map(s => ({ skill: s.skill, score: s.score })) };
          const mdWithRadar = hasRadar
            ? mdDeterministic
            : `${mdDeterministic}\n\n\`\`\`json\n${JSON.stringify(radarJson)}\n\`\`\`\n`;
          setIaReport(String(mdWithRadar));
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
          (Array.isArray(data.recommendations))
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


            const rec = ((data as { recommendations?: Record<string, unknown> })?.recommendations) || {} as Record<string, unknown>;

            // Preferir analysis_json (persistido por backend) como fuente única de verdad para puntuaciones 1–5
            const analysisJson: any = (data?.report?.cvAnalysis as any)?.analysis_json || null;
            if (analysisJson && (!analysisJson.overall || analysisJson.overall.score == null)) {
              throw new Error('Falta overall.score en analysis_json');
            }

            // Construir SIEMPRE el informe con tu formato deseado
            let markdown = buildDesiredMarkdown(data, String(dp.name || candidateName));
            // === NUEVO: añadir siempre bloque radarData para el extractor ===
            const radarJson = { radarData: (softSkillsToSend || []).map(s => ({ skill: s.skill, score: s.score })) };
            markdown += `\n\n\`\`\`json\n${JSON.stringify(radarJson)}\n\`\`\`\n`;
            setIaReport(markdown);
            if (import.meta.env.MODE !== 'production') {
              // eslint-disable-next-line no-console
              console.log('✅ DEBUG - Informe generado exitosamente. Longitud:', markdown.length);
              // eslint-disable-next-line no-console
              console.log('✅ DEBUG - Primeros 200 caracteres:', markdown.substring(0, 200));
            }
            // Frase motivacional final destacada (fuera del markdown principal)
            const frase = String((rec as any)['frase_final'] || '').trim();
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
        <div className="w-full md:w-1/2 h-96" ref={radarBoxRef}>
          <div className="screen-only h-full">
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
          {radarImg && (
            <img src={radarImg} alt="Mapa de habilidades" className="print-only w-full h-96 object-contain" />
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

      {/* Mensaje de error (solo si no hay informe generado) */}
      {errorIa && !iaReport && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-md p-6 mb-8" role="alert">
          <strong className="font-bold">Aviso.</strong>
          <span className="block sm:inline"> {errorIa}</span>
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
              
              {/* --- Bloque de estrellas del CV --- */}
              {(cvStarsLocal || (cvAnalysis as any)?.stars) && (
                <div className="cv-stars print-page-break-inside-avoid mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600">
                  <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">Diagnóstico del CV</h3>
                  <ul className="stars-list space-y-2">
                    {cvStarsLocal ? (
                      <>
                        <li className="flex items-center justify-between"><span className="font-medium text-gray-700 dark:text-gray-300">Formato:</span><span className="stars text-lg">{stars(cvStarsLocal.structure_score)}</span></li>
                        <li className="flex items-center justify-between"><span className="font-medium text-gray-700 dark:text-gray-300">Claridad:</span><span className="stars text-lg">{stars(cvStarsLocal.clarity_score)}</span></li>
                        <li className="flex items-center justify-between"><span className="font-medium text-gray-700 dark:text-gray-300">Coherencia:</span><span className="stars text-lg">{stars(cvStarsLocal.coherence_score)}</span></li>
                        <li className="flex items-center justify-between"><span className="font-medium text-gray-700 dark:text-gray-300">Información clave:</span><span className="stars text-lg">{stars(cvStarsLocal.key_info_score)}</span></li>
                        <li className="flex items-center justify-between"><span className="font-medium text-gray-700 dark:text-gray-300">Ortografía:</span><span className="stars text-lg">{stars(cvStarsLocal.spelling_style_score)}</span></li>
                      </>
                    ) : (
                      <>
                        <li className="flex items-center justify-between"><span className="font-medium text-gray-700 dark:text-gray-300">Formato:</span><span className="stars text-lg">{stars((cvAnalysis as any).stars?.formato)}</span></li>
                        <li className="flex items-center justify-between"><span className="font-medium text-gray-700 dark:text-gray-300">Claridad:</span><span className="stars text-lg">{stars((cvAnalysis as any).stars?.claridad)}</span></li>
                        <li className="flex items-center justify-between"><span className="font-medium text-gray-700 dark:text-gray-300">Coherencia:</span><span className="stars text-lg">{stars((cvAnalysis as any).stars?.coherencia)}</span></li>
                        <li className="flex items-center justify-between"><span className="font-medium text-gray-700 dark:text-gray-300">Información clave:</span><span className="stars text-lg">{stars((cvAnalysis as any).stars?.informacion_clave)}</span></li>
                        <li className="flex items-center justify-between"><span className="font-medium text-gray-700 dark:text-gray-300">Ortografía:</span><span className="stars text-lg">{stars((cvAnalysis as any).stars?.ortografia)}</span></li>
                      </>
                    )}
                  </ul>
                </div>
              )}

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
                    // Ejemplo de uso del diagnóstico con estrellas según checklist
                    // const dxFromReport: CvDiagnostico | undefined = (data?.report?.cvAnalysis as any)?.diagnostico_cv || undefined;
                    // if (dxFromReport) {
                    //   return <div>
                    //     <p><b>Formato:</b> <Stars n={dxFromReport.structure_score}/></p>
                    //     <p><b>Claridad:</b> <Stars n={dxFromReport.clarity_score}/></p>
                    //     <p><b>Coherencia:</b> <Stars n={dxFromReport.coherence_score}/></p>
                    //     <p><b>Información clave:</b> <Stars n={dxFromReport.key_info_score}/></p>
                    //     <p><b>Ortografía:</b> <Stars n={dxFromReport.spelling_style_score}/></p>
                    //   </div>
                    // }
                    
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
                          if (rawLabel && m[2]) {
                            const normLabel = rawLabel.startsWith('Ortografía') ? 'Ortografía' : rawLabel;
                            indicators.push({ label: normLabel, stars: m[2] });
                          }
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
                                      <span className="star-empty">
                                        {emptyStars}
                                      </span>
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
                                if (filledStars && emptyStars) {
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
            <div
              className="rounded-xl p-6 my-8 shadow-sm report-highlight border-2 bg-blue-50 border-blue-200 text-gray-800 dark:!bg-blue-800 dark:!border-blue-400 dark:!text-white print:bg-white print:text-black"
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
