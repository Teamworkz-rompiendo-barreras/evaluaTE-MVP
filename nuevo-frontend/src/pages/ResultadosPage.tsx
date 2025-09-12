/* eslint-disable no-console */
/* eslint-disable @typescript-eslint/no-explicit-any */
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
import type { CvAnalysis } from '@/types/report';
import '../styles/print.css';
import '../styles/report.css'; // Importar los nuevos estilos
import '../styles/stars.css'; // Importar estilos para estrellas
import { validateSoftSkills } from '../utils/debug-state';
import { filterValidSoftSkills } from '../utils/data-validation';
import { useDispatch } from 'react-redux';
import { generateFinalReport, saveCvAnalysis, saveSoftSkills } from '../features/personal/personalSlice';
import useCvRating from '../hooks/useCvRating';
import { convertBackendResponseToNewFormat, generateNewFormatReport } from '../config/reportConfig';

// Definir tipos locales para evitar importaciones problemáticas

// Tipos del rating del CV
type CvStars = 1|2|3|4|5;



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








const ResultadosPage: React.FC = () => {
  const dispatch = useDispatch();
  const personal = useAppSelector((state: RootState) => state.personal);
  const cvAnalysis: CvAnalysis | undefined = personal?.cvAnalysis;
  const report = personal?.report;
  const fecha = new Date().toLocaleDateString();
  const game = useAppSelector((state: RootState) => state.game);

  // Hook de valoración (alias para evitar choque de nombres)
  const uid = report?.userId ?? '';
  const rid = (report as any)?.id ?? '';
  const { rateCv: submitRating } = useCvRating(uid, rid);

  const asStars = (n: number): CvStars => (n < 1 ? 1 : n > 5 ? 5 : Math.round(n)) as CvStars;


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
  const fetchIaReportRef = useRef<() => Promise<void> | null>(null);
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
      
      // Asegurar análisis del CV si existe un archivo subido pero no hay análisis
      if (personal?.cvFile && !personal?.cvAnalysis) {
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

        const cvAnalysisPayload: CvAnalysis | null = cvAnalysis ? {
          structure_score: cvAnalysis.structure_score,
          coherence_score: cvAnalysis.coherence_score,
          key_info_score: cvAnalysis.key_info_score,
          clarity_score: cvAnalysis.clarity_score,
          style_score: cvAnalysis.style_score,
          evidence: cvAnalysis.evidence,
          corrections: cvAnalysis.corrections ?? [],
          reordering_suggestions: cvAnalysis.reordering_suggestions ?? [],
        } : null;

        const requestBody = {
          userId: report?.userId || 'user',
          fullName: userFullName,
          softSkills: softSkillsToSend,
          // Incluir contacto básico desde estado si el CV no lo trae
          email: personal.email || undefined,
          phone: personal.whatsapp || undefined,
          cvAnalysis: cvAnalysisPayload,
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
          const candidateName = String(data?.report?.fullName || userFullName);

          // Datos personales: preferir recomendaciones, luego report.ui y por último contact del CV
          const dpSrc = (data as { recommendations?: { datos_personales?: Record<string, unknown> }; report?: { ui?: { datos_personales?: Record<string, unknown> } } })?.recommendations?.datos_personales
            || (data as { report?: { ui?: { datos_personales?: Record<string, unknown> } } })?.report?.ui?.datos_personales
            || {} as Record<string, unknown>;
          const dp = {
            name: (dpSrc?.['name'] as string) || candidateName,
            location: (dpSrc?.['location'] as string) || 'No consta',
            email: (dpSrc?.['email'] as string) || '',
            phone: (dpSrc?.['phone'] as string) || 'No especificado',
            disability_certificate: (dpSrc?.['disability_certificate'] != null)
              ? (dpSrc['disability_certificate'] as string)
              : ((report?.jobPreferences as any)?.hasDisabilityCert ? 'Sí' : 'No')
          };

          let normalized;
          try {
            normalized = convertBackendResponseToNewFormat(data);
          } catch (error) {
            if (import.meta.env.MODE !== 'production') {
              // eslint-disable-next-line no-console
              console.warn('⚠️ Error generando informe:', error);
            }
            setErrorIa('No se pudo generar el informe IA. Intenta nuevamente.');
            setFinalPhrase('');
            return;
          }

          const essentialFilled = normalized.summary && normalized.profile_summary && normalized.personal_data;
          if (!essentialFilled) {
            console.warn('⚠️ Respuesta del backend con campos esenciales vacíos', normalized);
            setErrorIa('El informe recibido está incompleto. Intenta nuevamente.');
            setFinalPhrase('');
            return;
          }

          const markdown = generateNewFormatReport(normalized);
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
        setFinalPhrase('');
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
    fetchIaReportRef.current = fetchIaReport;
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

  const handleRetry = () => {
    if (loadingIa) return;
    setErrorIa('');
    fetchIaReportRef.current?.();
  };

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
    if (!cvAnalysis) return null;

    const formatScore = asStars(cvAnalysis.structure_score);
    const clarityScore = asStars(cvAnalysis.clarity_score);
    const coherenceScore = asStars(cvAnalysis.coherence_score);
    const keyInfoScore = asStars(cvAnalysis.key_info_score);
    const styleScore = asStars(cvAnalysis.style_score);

    const { evidence, corrections = [], reordering_suggestions = [] } = cvAnalysis;

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
                <span className="font-semibold text-gray-900 dark:text-gray-800">Estilo:</span>
                <span className="text-lg"><StarsGold n={styleScore} /></span>
              </div>
            </div>
          </div>
        </div>

        {/* Observaciones del análisis */}
        {evidence && (
          <div className="mb-4">
            <p className="font-semibold mb-2 text-gray-900 dark:text-gray-100">Observaciones del análisis:</p>
            <ul className="list-disc list-inside space-y-1 text-gray-900 dark:text-gray-100">
              <li className="text-gray-900 dark:text-gray-100"><strong className="font-semibold">Formato:</strong> {evidence.structure}</li>
              <li className="text-gray-900 dark:text-gray-100"><strong className="font-semibold">Coherencia:</strong> {evidence.coherence}</li>
              <li className="text-gray-900 dark:text-gray-100"><strong className="font-semibold">Información clave:</strong> {evidence.key_info}</li>
              <li className="text-gray-900 dark:text-gray-100"><strong className="font-semibold">Claridad:</strong> {evidence.clarity}</li>
              <li className="text-gray-900 dark:text-gray-100"><strong className="font-semibold">Estilo:</strong> {evidence.style}</li>
            </ul>
          </div>
        )}

        {/* Correcciones/Acciones sugeridas */}
        {corrections.length > 0 && (
          <div className="mb-4">
            <p className="font-semibold mb-2 text-gray-900 dark:text-gray-100">Correcciones/Acciones:</p>
            <ul className="list-disc list-inside space-y-1 text-gray-900 dark:text-gray-100">
              {corrections.map((correction, i) => (
                <li key={i} className={`text-gray-900 dark:text-gray-100 ${i === 0 ? 'mt-0' : ''}`}>{correction}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Reordenación sugerida */}
        {reordering_suggestions.length > 0 && (
          <div className="mb-4">
            <p className="font-semibold mb-2 text-gray-900 dark:text-gray-100">Reordenación sugerida:</p>
            <ul className="list-disc list-inside space-y-1 text-gray-900 dark:text-gray-100">
              {reordering_suggestions.map((suggestion, i) => (
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
          <div className="mt-4">
            <button
              onClick={handleRetry}
              className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
            >
              Reintentar
            </button>
          </div>
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
