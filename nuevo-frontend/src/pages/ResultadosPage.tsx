/* eslint-disable no-console */
/* eslint-disable @typescript-eslint/no-explicit-any */
// src/pages/ResultadosPage.tsx

import React, { useEffect, useState, useRef, useMemo } from 'react';
import processRadarData from './processRadarData';
import { useAppSelector } from '../app/hooks';
import type { RootState } from '../app/store';
import { ResponsiveRadar } from '@nivo/radar';
import logo from '../assets/Logo_teamworkz.png';
import '../styles/print.css';
import '../styles/report.css';
import '../styles/stars.css';
import { filterValidSoftSkills } from '../utils/data-validation';
import useCvRating from '../hooks/useCvRating';
import { useAuth } from '../context/AuthContext';
import { useLocation } from 'react-router-dom';
import { API_CONFIG } from '../config/api';
import { GAME_NAME_MAP } from '../config/reportConfig';

interface AdvancedReport {
  datos_personales: Record<string, string>;
  resumen_ejecutivo: string;
  puntuacion_global: number;
  interpretacion_global: string;
  perfil_competencias: Array<{ categoria: string, competencias: Array<{nombre: string, puntuacion: number, nivel: string, explicacion: string}> }>;
  fortalezas_principales: Array<{nombre: string, explicacion_practica: string}>;
  areas_mejora: Array<{nombre: string, porque_afecta: string, como_mejorar: string, acciones_concretas: string[]}>;
  analisis_cv: {
    resumen: string;
    experiencia: string[];
    formacion: string[];
    idiomas: string[];
    software: string[];
    valoraciones: {formato: number, claridad: number, coherencia: number, info_clave: number, ortografia: number};
    puntos_fuertes: string[];
    aspectos_mejorar: string[];
    ats_compatibilidad: number;
    ats_explicacion: string;
  };
  entornos_ideales: string[];
  roles_recomendados: Array<{titulo: string, nivel: string, modalidad: string, por_que_encaja: string, demanda_laboral: string}>;
  plan_accion: {dias_30: string[], dias_60: string[], dias_90: string[]};
  estrategia_busqueda: string[];
  herramientas_recomendadas: Array<{nombre: string, para_que_sirve: string}>;
  resultados_juegos: Array<{juego: string, que_mide: string, resultado: string, interpretacion: string, aplicacion_entrevista: string}>;
  recomendaciones_personalizadas: string[];
  recursos_adicionales: Array<{nombre: string, tipo: string, descripcion: string}>;
  mensaje_final: string;
}

type CvStars = 1 | 2 | 3 | 4 | 5;

const safeArray = (arr: any): any[] => Array.isArray(arr) ? arr : [];

const formatText = (text: any) => {
  if (text === null || text === undefined || text === '') return null;
  
  let safeText = '';
  if (typeof text === 'string') {
    safeText = text;
  } else if (typeof text === 'object') {
    const values = Object.values(text);
    safeText = values.filter(v => typeof v === 'string').join(': ') || JSON.stringify(text);
  } else {
    safeText = String(text);
  }

  const parts = safeText.split(/(\*\*.*?\*\*)/g);
  return (
    <span className="inline">
      {parts.map((part, index) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          const cleanText = part.replace(/\*\*/g, '');
          return <strong key={index} className="font-bold text-inherit">{cleanText}</strong>;
        }
        return <React.Fragment key={index}>{part}</React.Fragment>;
      })}
    </span>
  );
};

const StarsGold: React.FC<{ n: any }> = ({ n }) => {
  const num = typeof n === 'number' ? n : Number(n);
  const safeN = isNaN(num) ? 3 : Math.max(1, Math.min(5, Math.round(num)));
  const filled = "★".repeat(safeN);
  const empty = "★".repeat(5 - safeN);
  return (
    <span role="img" aria-label={`${safeN} de 5 estrellas`} className="inline-flex tracking-widest">
      <span className="text-[#374BA6] font-bold text-lg" aria-hidden="true">{filled}</span>
      <span className="text-slate-400 font-bold text-lg" aria-hidden="true">{empty}</span>
    </span>
  );
};

const formatGameName = (value: any) => {
  const raw = typeof value === 'string' ? value.trim() : '';
  if (!raw) return '';
  if (GAME_NAME_MAP[raw]) return GAME_NAME_MAP[raw];

  const normalized = raw
    .replace(/[_-]+/g, ' ')
    .trim();

  if (!normalized) return raw;
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
};

export default function ResultadosPage() {
  const { loading: authLoading } = useAuth(); 
  const location = useLocation();
  const personal = useAppSelector((state: RootState) => state.personal);
  const game = useAppSelector((state: RootState) => state.game);
  const rawReportFromUpload = location.state?.rawReport;
  
  const initialData = rawReportFromUpload || null;
  
  const [reportData, setReportData] = useState<AdvancedReport | null>(initialData);
  const [loadingIa, setLoadingIa] = useState<boolean>(false);
  const [loadingMessage, setLoadingMessage] = useState<string>('Autenticando sesión segura...');
  const [errorIa, setErrorIa] = useState<string>('');
  
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [pdfExportError, setPdfExportError] = useState<string>('');
  const [pdfGenerationMessage, setPdfGenerationMessage] = useState<string>('Preparando el documento...');
  const [exportEta, setExportEta] = useState<number | null>(null);
  const [exportProgress, setExportProgress] = useState<number>(0);
  const exportIntervalRef = useRef<number | null>(null);
  
  const [retryCount, setRetryCount] = useState<number>(0);
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  
  const reportRef = useRef<HTMLDivElement>(null);
  const isFetchingRef = useRef(false) as React.MutableRefObject<boolean>;
  
  const [feedback, setFeedback] = useState<{ rating: string, comment: string }>({ rating: '', comment: '' });
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackError, setFeedbackError] = useState('');
  
  const { rateCv: submitRating } = useCvRating(personal?.report?.userId ?? '', (personal?.report as any)?.id ?? '');

  const asStars = (n: number): CvStars => (n < 1 ? 1 : n > 5 ? 5 : Math.round(n)) as CvStars;

  const softSkillsData = useMemo(() => {
    const allCombinedSkillsMap = new Map();
    [...safeArray(personal?.softSkills), ...safeArray(game?.softSkills)].forEach(rawSkill => {
      const s = rawSkill as any;
      const skillName = s?.skill || s?.name || s?.softSkill;
      if (s && skillName) {
        const key = String(skillName).toLowerCase().trim();
        if (!allCombinedSkillsMap.has(key) || (Number(s.score) || 0) > (Number(allCombinedSkillsMap.get(key)?.score) || 0)) {
          allCombinedSkillsMap.set(key, { ...s, skill: skillName });
        }
      }
    });
    return filterValidSoftSkills(Array.from(allCombinedSkillsMap.values()));
  }, [personal?.softSkills, game?.softSkills]);

  useEffect(() => {
    if (isExportingPdf) {
      const estimated = 15; // initial ETA in seconds
      setExportEta(estimated);
      setExportProgress(5);
      // increment progress and decrement ETA
      exportIntervalRef.current = window.setInterval(() => {
        setExportEta(prev => (prev === null ? null : Math.max(0, prev - 1)));
        setExportProgress(prev => Math.min(95, Math.round(prev + Math.random() * 8 + 3)));
      }, 1000) as unknown as number;
    } else {
      if (exportIntervalRef.current) {
        clearInterval(exportIntervalRef.current);
        exportIntervalRef.current = null;
      }
      if (exportProgress > 0) setExportProgress(100);
      setTimeout(() => {
        setExportEta(null);
        setExportProgress(0);
      }, 800);
    }
    return () => {
      if (exportIntervalRef.current) {
        clearInterval(exportIntervalRef.current);
        exportIntervalRef.current = null;
      }
    };
  }, [isExportingPdf]);

  const radarData = useMemo(() => {
    const combined = softSkillsData.map(s => ({ softskill: s.skill as string, score: Number(s.score) || 0 }));
    return processRadarData(combined);
  }, [softSkillsData]);

  const safeRadarData = useMemo(() => {
    if (!Array.isArray(radarData)) return [];
    const sanitized = radarData.filter((item: any) => item && typeof item.softskill === 'string' && item.softskill.trim() !== '');
    return sanitized;
  }, [radarData]);

  const hasAnyRadarValue = safeRadarData.length >= 3 && safeRadarData.some((item: any) => Number(item?.score) > 0);

  const candidateName = useMemo(() => {
    if (personal?.firstName) {
      return `${personal.firstName} ${personal.lastName || ''}`.trim();
    }
    return reportData?.datos_personales?.['Nombre'] || reportData?.datos_personales?.['nombre'] || 'Candidato';
  }, [personal, reportData]);

  const displayPersonalData = useMemo(() => {
    const result: Record<string, string> = { 'NOMBRE COMPLETO': candidateName };

    if (!reportData?.datos_personales || typeof reportData.datos_personales !== 'object' || Array.isArray(reportData.datos_personales)) {
        return result;
    }
    
    Object.entries(reportData.datos_personales).forEach(([key, value]) => {
      if (key.toLowerCase() !== 'nombre') {
        result[key.toUpperCase()] = String(value || '-');
      }
    });
    return result;
  }, [reportData, candidateName]);

  useEffect(() => {
    (window as any).__rateCv = (v: number) => submitRating(asStars(v));
    return () => { try { delete (window as any).__rateCv; } catch { /* no-op */ } };
  }, [submitRating]);

  useEffect(() => {
    if (initialData || reportData) return; 
    if (authLoading || !personal || !game) return;
    
    const fetchIaReport = async () => {
      if (isFetchingRef.current) return;
      isFetchingRef.current = true;
      setLoadingIa(true);
      setErrorIa('');
      
      try {
        const envBaseUrl = API_CONFIG.BASE_URL || 'http://localhost:8080';
        const baseUrl = envBaseUrl.replace(/\/$/, '');

        setLoadingMessage('Estableciendo conexión encriptada...');
        const authResponse = await fetch(`${baseUrl}/api/auth/guest-token`, { method: 'POST' });
        
        if (!authResponse.ok) {
            const errData = await authResponse.json().catch(() => ({}));
            throw new Error(errData.detail || 'Fallo al validar credenciales de seguridad (401).');
        }
        
        const authData = await authResponse.json();
        const token = authData.access_token;
        setSessionToken(token);

        setLoadingMessage('Transmitiendo expediente al clúster de IA...');
        const formData = new FormData();
        formData.append("game_results", JSON.stringify({ completedGames: game.completedGames, softSkills: softSkillsData }));
        
        const rawPrefs = personal.jobPreferences;
        const safePreferences: Record<string, any> = (typeof rawPrefs === 'object' && rawPrefs !== null && !Array.isArray(rawPrefs)) 
            ? (rawPrefs as Record<string, any>) : {};

        const jobTarget =
            safePreferences['desired_roles'] ??
            safePreferences['desiredRoles'] ??
            safePreferences['role'] ??
            safePreferences['target_role'] ??
            (Array.isArray(safePreferences['areas']) ? safePreferences['areas'][0] : undefined) ??
            (typeof rawPrefs === 'string' ? rawPrefs : undefined) ??
            personal.jobPreferences;

        const normalizedRoleList = Array.isArray(jobTarget)
            ? jobTarget.filter(Boolean)
            : jobTarget ? [String(jobTarget)] : [];

        formData.append("preferences", JSON.stringify({
          ...safePreferences,
          desired_roles: normalizedRoleList,
          desiredRoles: normalizedRoleList,
          workMode: personal.workMode ?? safePreferences['workMode'] ?? safePreferences['work_mode'] ?? 'remoto',
          work_mode: personal.workMode ?? safePreferences['workMode'] ?? safePreferences['work_mode'] ?? 'remoto',
          fullName: `${personal.firstName || ''} ${personal.lastName || ''}`.trim(),
          dataConsent: Boolean(personal.dataConsent),
          gdprConsent: Boolean(personal.gdprConsent),
        }));
        
        if (personal.cvAnalysis) formData.append("cv_analysis", JSON.stringify(personal.cvAnalysis));
        if (personal.cvFile && personal.cvFile.fileContent) {
          try {
            const fileResponse = await fetch(personal.cvFile.fileContent);
            const blob = await fileResponse.blob();
            formData.append("cv_file", blob, personal.cvFile.fileName || "curriculum.pdf");
          } catch (blobError) {
            console.error("Fallo reconstrucción física de archivo local:", blobError);
          }
        }

        const response = await fetch(`${baseUrl}/api/analyze`, {
            method: 'POST',
            body: formData,
            headers: { 'Authorization': `Bearer ${token}` },
        });

        if (response.status === 401) throw new Error('Acceso denegado: Sesión expirada.');
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Error de infraestructura (${response.status})`);
        }

        const enqueueData = await response.json();
        const jobId = enqueueData.job_id;

        if (!jobId) throw new Error('El servidor no devolvió un identificador de tarea válido.');

        setLoadingMessage('Evaluación en curso. Este análisis es profundo y puede tardar entre 1 y 3 minutos. Por favor, no cierre esta ventana...');

        const pollStatus = async () => {
            try {
                const statusRes = await fetch(`${baseUrl}/api/report/status/${jobId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (statusRes.status === 401) throw new Error('La sesión de consulta ha caducado por inactividad.');
                if (!statusRes.ok) {
                    const errorData = await statusRes.json().catch(() => ({}));
                    throw new Error(errorData.detail || 'Error de red al consultar el estado del informe.');
                }

                const statusData = await statusRes.json();

                if (statusData.status === 'completado') {
                    setReportData(statusData.report as AdvancedReport);
                    setLoadingIa(false);
                    isFetchingRef.current = false;
                } else if (statusData.status === 'error') {
                    throw new Error(statusData.error || 'Fallo crítico en el motor asíncrono.');
                } else {
                    if (statusData.progress) setLoadingMessage(statusData.progress);
                    setTimeout(pollStatus, 3000);
                }
            } catch (err: any) {
                setErrorIa(err.message || 'Pérdida de conexión durante la espera.');
                setLoadingIa(false);
                isFetchingRef.current = false;
            }
        };

        setTimeout(pollStatus, 3000);

      } catch (err: any) {
        setErrorIa(err.message || 'Error crítico al orquestar el análisis.');
        setLoadingIa(false);
        isFetchingRef.current = false;
      }
    };
    
    fetchIaReport();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialData, authLoading, retryCount]);

  const handleDownloadPdf = async () => {
    const element = reportRef.current;
    if (!element) return;
    
    setIsExportingPdf(true);
    setPdfGenerationMessage('Generando PDF... Este proceso puede tardar unos segundos.');
    setPdfExportError('');
    
    let currentToken = sessionToken;
    const envBaseUrl = API_CONFIG.BASE_URL || 'http://localhost:8080';
    const baseUrl = envBaseUrl.replace(/\/$/, '');
    
    if (!currentToken) {
        try {
            const authRes = await fetch(`${baseUrl}/api/auth/guest-token`, { method: 'POST' });
            if (!authRes.ok) throw new Error('Fallo Auth');
            const authData = await authRes.json();
            currentToken = authData.access_token;
            setSessionToken(currentToken);
        } catch {
            setPdfExportError("No se pudo establecer conexión segura para la exportación.");
            setIsExportingPdf(false);
            return;
        }
    }

    const htmlEl = document.documentElement;
    const wasDark = htmlEl.classList.contains('dark');
    if (wasDark) htmlEl.classList.remove('dark');
    
    try {
      const htmlContent = element.outerHTML;
      const response = await fetch(`${baseUrl}/api/export-pdf`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json', 
            'Authorization': `Bearer ${currentToken}` 
        },
        body: JSON.stringify({ html_content: htmlContent })
      });

      if (response.status === 401) throw new Error('Sesión de exportación caducada.');
      if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || 'El microservicio no pudo completar la solicitud.');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Informe_Profesional_${candidateName.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch (error: any) {
      console.error("Fallo exportación PDF:", error);
      setPdfExportError(`Error de seguridad o conectividad: ${error.message || 'No se pudo generar el documento.'}`);
    } finally {
      if (wasDark) htmlEl.classList.add('dark');
      setIsExportingPdf(false);
      setPdfGenerationMessage('Documento listo para descarga.');
    }
  };

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedbackError('');
    if (!sessionToken) {
        setFeedbackError('Sesión no válida para enviar feedback.');
        return;
    }
    try {
      const envBaseUrl = API_CONFIG.BASE_URL || 'http://localhost:8080';
      const baseUrl = envBaseUrl.replace(/\/$/, '');
      const res = await fetch(`${baseUrl}/api/informe-ia/feedback`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionToken}`
        },
        body: JSON.stringify({ informe: reportData?.resumen_ejecutivo || "N/A", rating: feedback.rating, comment: feedback.comment })
      });
      
      if (res.status === 401) {
          setFeedbackError('Sesión caducada.');
      } else if (res.ok) {
          setFeedbackSent(true);
      } else {
          const errorData = await res.json().catch(() => ({}));
          setFeedbackError(errorData.detail || 'No se pudo registrar la valoración.');
      }
    } catch { 
      setFeedbackError('Error de red. Servidor inactivo.'); 
    }
  };

  if (loadingIa && !reportData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-slate-900 px-4">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-[#374BA6] dark:border-blue-400"></div>
        {/* WCAG 2.2 AA (4.1.3): aria-live="polite" dinámico para lecturas asíncronas */}
        <div className="text-center mt-6" aria-live="polite" aria-atomic="true" role="status">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">{loadingMessage}</h2>
          <p className="text-base font-medium text-gray-600 dark:text-slate-300 mt-2">
            Este proceso requiere un análisis profundo. Puede navegar por otras ventanas, le avisaremos cuando finalice.
          </p>
        </div>
      </div>
    );
  }

  if (errorIa && !reportData) {
    return (
      <div className="max-w-2xl mx-auto mt-20 bg-red-50 dark:bg-slate-800 border-l-4 border-red-500 p-6 rounded shadow-lg" role="alert" aria-live="assertive">
        <h3 className="text-lg font-bold text-red-800 dark:text-red-200 mb-2">Error de Procesamiento</h3>
        <p className="text-red-700 dark:text-slate-100 mb-4 break-words">{errorIa}</p>
        <button 
          onClick={() => { isFetchingRef.current = false; setRetryCount(prev => prev + 1); }} 
          className="bg-red-700 hover:bg-red-800 text-white font-bold py-2 px-6 rounded transition focus:ring-4 focus:ring-red-300"
        >
          Reintentar Proceso
        </button>
      </div>
    );
  }

  if (!reportData) return null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 py-8 font-sans text-gray-900 dark:text-slate-50 print:bg-white print:py-0">
      {/* Overlay modal to reassure users while PDF is being generated */}
      {isExportingPdf && (
        <div
          role="status"
          aria-live="polite"
          aria-atomic="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
        >
          <div className="bg-white dark:bg-slate-800 text-gray-900 dark:text-white rounded-lg shadow-lg p-6 max-w-xl w-full flex items-center gap-4">
            <div className="flex-shrink-0">
              <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full" aria-hidden="true"></div>
            </div>
            <div className="flex-1">
              <p className="text-lg font-semibold">Generando tu documento PDF…</p>
              <p className="text-sm text-slate-600 dark:text-slate-300 mt-1">{pdfGenerationMessage || 'Este proceso puede tardar unos segundos. No cierre esta ventana.'}</p>

              <div className="mt-4" aria-hidden={exportEta === null}>
                <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-3 overflow-hidden">
                  <div
                    className="h-3 bg-blue-600 dark:bg-blue-400 transition-all"
                    style={{ width: `${exportProgress}%` }}
                    role="progressbar"
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-valuenow={exportProgress}
                  />
                </div>
                <div className="text-xs text-gray-600 dark:text-slate-300 mt-2">
                  {exportEta !== null ? (
                    <span>Aprox. {exportEta}s restantes</span>
                  ) : (
                    <span>Preparando descarga…</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      <div ref={reportRef} id="reporte-analisis" className="max-w-[210mm] mx-auto bg-white dark:bg-slate-800 print:shadow-none shadow-xl border border-gray-200/60 dark:border-slate-700 overflow-hidden w-full print:border-gray-200">
        
        <header className="bg-[#374BA6] dark:bg-slate-950 text-white p-16 flex flex-col items-center justify-center text-center relative print:bg-[#374BA6] print:h-[290mm]">
          <img src={logo} alt="Teamworkz - Rompiendo Barreras" className="h-16 mb-12 brightness-0 invert" aria-hidden="true" />
          <h1 className="text-5xl font-black tracking-tight mb-6 leading-tight text-white">Informe Profesional<br/>de Empleabilidad</h1>
          <h2 className="text-md uppercase tracking-[0.4em] font-bold text-blue-200 mb-4">EvalúaTE</h2>
          <p className="text-lg text-blue-100 font-medium mb-20">Consultoría de Talento Corporativo y Estrategia Laboral</p>
          <div className="bg-white/10 dark:bg-slate-800/80 backdrop-blur-md px-12 py-6 rounded-xl border border-white/10 w-full max-w-md">
            <p className="text-sm text-blue-200 font-semibold mb-1">{new Date().toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
            <h2 className="text-3xl font-bold tracking-tight text-white">{candidateName}</h2>
          </div>
        </header>

        <div className="html2pdf__page-break"></div>

        <main className="p-12 space-y-12 print:p-10">
          <section aria-labelledby="indice-global" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <div className="flex flex-col items-center bg-gray-50 dark:bg-slate-900 rounded-xl p-8 border border-gray-200/50 dark:border-slate-600">
              <span id="indice-global" className="text-xs font-bold uppercase tracking-wider text-[#374BA6] dark:text-blue-300 block mb-2">Índice Global</span>
              <div className="text-6xl font-black text-gray-900 dark:text-white tabular-nums mb-4" aria-label={`Puntuación de empleabilidad: ${reportData.puntuacion_global || 0} de 100`}>
                {reportData.puntuacion_global || 0}<span className="text-2xl text-gray-600 dark:text-slate-300 font-normal" aria-hidden="true">/100</span>
              </div>
              <p className="text-gray-700 dark:text-slate-100 leading-relaxed font-semibold text-sm text-justify">
                {formatText(reportData.interpretacion_global)}
              </p>
            </div>
          </section>

          <section aria-labelledby="resumen-ejecutivo" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="resumen-ejecutivo" className="text-lg font-bold text-[#374BA6] dark:text-blue-300 pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/10">1. Resumen Ejecutivo</h2>
            <p className="text-sm leading-relaxed text-gray-700 dark:text-slate-100 text-justify font-medium">
              {formatText(reportData.resumen_ejecutivo)}
            </p>
          </section>

          <section aria-labelledby="perfil-personal" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="perfil-personal" className="text-lg font-bold text-[#374BA6] dark:text-blue-300 pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/10">2. Perfil Personal</h2>
            <div className="flex flex-wrap gap-4">
              {Object.entries(displayPersonalData).map(([key, value]) => (
                <div key={key} className="flex-1 min-w-[150px] bg-gray-50/80 dark:bg-slate-900 p-3 rounded border border-gray-100 dark:border-slate-600">
                  <p className="text-[10px] font-bold text-gray-600 dark:text-slate-300 uppercase tracking-widest mb-0.5">{key}</p>
                  <p className="text-xs font-bold text-gray-900 dark:text-white truncate" title={String(value)}>{String(value) || '-'}</p>
                </div>
              ))}
            </div>
          </section>

          <div className="html2pdf__page-break"></div>

          <section aria-labelledby="perfil-competencias" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="perfil-competencias" className="text-lg font-bold text-[#374BA6] dark:text-blue-300 pb-2 mb-6 uppercase tracking-wider border-b border-[#374BA6]/10">3. Perfil de Competencias</h2>
            <div style={{ width: '600px', height: '480px', margin: '0 auto', display: 'block', position: 'relative' }} className="nivo-radar-wrapper bg-white dark:bg-slate-900 mb-8 border border-gray-50 dark:border-slate-600 rounded-xl" aria-hidden="true">
              <style dangerouslySetInnerHTML={{__html: `
                .dark .nivo-radar-wrapper text { fill: #ffffff !important; font-weight: 700 !important; font-size: 11px !important; }
                .dark .nivo-radar-wrapper line, .dark .nivo-radar-wrapper path[stroke-dasharray] { stroke: #64748b !important; }
                .dark .nivo-radar-wrapper path:not([stroke-dasharray]) { fill: #3b82f6 !important; fill-opacity: 0.4 !important; stroke: #93c5fd !important; stroke-width: 2px !important; }
                .dark .nivo-radar-wrapper circle { fill: #0f172a !important; stroke: #93c5fd !important; stroke-width: 2px !important; r: 4 !important; }
              `}} />
              {hasAnyRadarValue ? (
                <ResponsiveRadar
                  data={safeRadarData as unknown as Array<Record<string, unknown>>}
                  keys={["score"]}
                  indexBy="softskill"
                  margin={{ top: 70, right: 140, bottom: 70, left: 140 }}
                  maxValue={100}
                  gridLevels={5}
                  theme={{
                    text: { fill: 'var(--radar-text-color, #1e293b)', fontSize: 10, fontWeight: 700 },
                    grid: { line: { stroke: 'var(--radar-grid-color, #cbd5e1)', strokeWidth: 1, strokeDasharray: "3 3" } }
                  }}
                  borderColor="#374BA6"
                  gridLabelOffset={22}
                  dotSize={8}
                  dotColor="#ffffff"
                  dotBorderWidth={3}
                  dotBorderColor="#374BA6"
                  colors={["#374BA6"]}
                  fillOpacity={0.2}
                  animate={false}
                  isInteractive={false}
                />
              ) : (
                <p className="text-gray-600 dark:text-slate-300 italic text-xs text-center mt-20">Datos no disponibles para graficar.</p>
              )}
            </div>

            {/* WCAG 2.2 AA (1.1.1): TABLA OCULTA SEMÁNTICA GARANTIZADA PARA LECTORES DE PANTALLA */}
            <table className="sr-only">
              <caption>Puntuación detallada del perfil de competencias (gráfico de radar)</caption>
              <thead>
                <tr><th scope="col">Competencia</th><th scope="col">Puntuación (sobre 100)</th></tr>
              </thead>
              <tbody>
                {safeRadarData.length > 0 ? (
                  safeRadarData.map((item: any, i: number) => (
                    <tr key={i}><td>{item.softskill}</td><td>{item.score}</td></tr>
                  ))
                ) : (
                  <tr><td colSpan={2}>No hay datos de competencias registrados para esta evaluación.</td></tr>
                )}
              </tbody>
            </table>

            <div className="flex flex-col space-y-8 mt-6 w-full">
              {safeArray(reportData.perfil_competencias).map((grupo, idx) => (
                <div key={idx} className="break-inside-avoid w-full">
                  <h3 className="text-xs font-bold text-gray-600 dark:text-slate-300 uppercase tracking-widest mb-4 border-l-4 border-[#374BA6] pl-2 bg-gray-50/50 dark:bg-slate-900 py-1.5">{formatText(grupo.categoria)}</h3>
                  <div className="flex flex-col space-y-5 w-full">
                    {safeArray(grupo.competencias).map((comp, cIdx) => (
                      <div key={cIdx} className="border-b border-gray-50 dark:border-slate-700 pb-3 last:border-0 w-full">
                        <div className="flex justify-between items-end mb-1">
                          <span className="text-sm font-bold text-gray-800 dark:text-white">{formatText(comp.nombre)}</span>
                          <span className="text-[10px] font-black text-[#374BA6] dark:text-slate-900 bg-blue-50 dark:bg-blue-200 px-2 py-0.5 rounded">{comp.puntuacion || 0}/100</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-1.5 mb-2" aria-hidden="true">
                          <div className="bg-[#374BA6] dark:bg-blue-400 h-1.5 rounded-full" style={{ width: `${comp.puntuacion || 0}%` }}></div>
                        </div>
                        <p className="text-xs text-gray-700 dark:text-slate-100 leading-relaxed text-justify">{formatText(comp.explicacion)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>

          <div className="html2pdf__page-break"></div>

          <section aria-labelledby="fortalezas-principales" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="fortalezas-principales" className="text-lg font-bold text-emerald-700 dark:text-emerald-300 pb-2 mb-4 uppercase tracking-wider border-b border-emerald-100 dark:border-slate-600">4. Fortalezas Principales</h2>
            <div className="flex flex-col space-y-4 w-full">
              {safeArray(reportData.fortalezas_principales).map((f, idx) => (
                <div key={idx} className="bg-emerald-50/40 dark:bg-slate-900 p-5 rounded-lg border-l-4 border-emerald-500 w-full">
                  <h3 className="text-sm font-bold text-emerald-900 dark:text-emerald-200 mb-2 uppercase tracking-wider">{formatText(f.nombre)}</h3>
                  <p className="text-xs text-emerald-800 dark:text-slate-100 leading-relaxed text-justify">{formatText(f.explicacion_practica)}</p>
                </div>
              ))}
            </div>
          </section>

          <section aria-labelledby="areas-mejora" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="areas-mejora" className="text-lg font-bold text-amber-600 dark:text-amber-300 pb-2 mb-4 uppercase tracking-wider border-b border-amber-100 dark:border-slate-600">5. Áreas de Mejora</h2>
            <div className="flex flex-col space-y-4 w-full">
              {safeArray(reportData.areas_mejora).map((m, idx) => (
                <div key={idx} className="bg-amber-50/30 dark:bg-slate-900 p-5 rounded-lg border-l-4 border-amber-500 w-full">
                  <h3 className="text-sm font-bold text-amber-900 dark:text-amber-200 mb-2 uppercase tracking-wider">{formatText(m.nombre)}</h3>
                  <p className="text-xs text-amber-800 dark:text-slate-100 mb-3 text-justify">{formatText(m.porque_afecta)}</p>
                  <div className="mt-3 pt-3 border-t border-amber-200/50 dark:border-amber-700/50">
                    <p className="text-[10px] font-bold text-amber-900 dark:text-amber-200 uppercase tracking-widest mb-2">Plan de capacitación inmediata:</p>
                    <ul className="list-disc list-inside text-xs text-amber-800 dark:text-slate-100 space-y-1.5">
                      {safeArray(m.acciones_concretas).map((acc, aIdx) => <li key={aIdx} className="text-justify">{formatText(acc)}</li>)}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <div className="html2pdf__page-break"></div>

          <section aria-labelledby="analisis-cv" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="analisis-cv" className="text-lg font-bold text-[#374BA6] dark:text-blue-300 pb-2 mb-6 uppercase tracking-wider border-b border-[#374BA6]/10">6. Análisis Profesional del CV</h2>
            <div className="flex flex-col items-center gap-4 mb-8 bg-gray-50 dark:bg-slate-900 p-6 rounded-xl border border-gray-100 dark:border-slate-600 w-full">
              <div className="flex flex-col items-center justify-center w-full max-w-[200px] bg-white dark:bg-slate-800 p-4 rounded-lg border border-gray-200/60 dark:border-slate-600">
                <span className="text-[10px] font-bold text-gray-600 dark:text-slate-300 uppercase tracking-widest text-center">ATS MATCH</span>
                <div className="text-4xl font-black text-[#374BA6] dark:text-blue-300 my-1">{reportData.analisis_cv?.ats_compatibilidad || 0}%</div>
                <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-1.5" aria-hidden="true">
                  <div className="h-1.5 rounded-full bg-[#374BA6] dark:bg-blue-400" style={{ width: `${reportData.analisis_cv?.ats_compatibilidad || 0}%` }}></div>
                </div>
              </div>
              <p className="text-sm text-gray-700 dark:text-slate-100 italic border-l-4 border-gray-400 dark:border-slate-500 pl-4 text-justify mt-2">"{formatText(reportData.analisis_cv?.resumen)}"</p>
            </div>
            
            <div className="flex flex-col space-y-6 w-full">
              <div>
                <h3 className="font-bold text-gray-600 dark:text-slate-300 uppercase text-xs tracking-wider mb-3">Métricas de Documentación</h3>
                <ul className="space-y-2 bg-gray-50/50 dark:bg-slate-900 p-4 rounded-lg border border-gray-200 dark:border-slate-600">
                  <li className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-2">
                    <span className="text-sm font-semibold text-gray-700 dark:text-slate-100">Formato Estructural</span> <StarsGold n={reportData.analisis_cv?.valoraciones?.formato} />
                  </li>
                  <li className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-2">
                    <span className="text-sm font-semibold text-gray-700 dark:text-slate-100">Claridad Narrativa</span> <StarsGold n={reportData.analisis_cv?.valoraciones?.claridad} />
                  </li>
                  <li className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-2">
                    <span className="text-sm font-semibold text-gray-700 dark:text-slate-100">Coherencia de Trayectoria</span> <StarsGold n={reportData.analisis_cv?.valoraciones?.coherencia} />
                  </li>
                  <li className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-2">
                    <span className="text-sm font-semibold text-gray-700 dark:text-slate-100">Información de Impacto Clave</span> <StarsGold n={reportData.analisis_cv?.valoraciones?.info_clave} />
                  </li>
                  <li className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-gray-700 dark:text-slate-100">Léxico y Ortografía</span> <StarsGold n={reportData.analisis_cv?.valoraciones?.ortografia} />
                  </li>
                </ul>
              </div>
              
              <div className="bg-emerald-50/40 dark:bg-slate-900 p-4 rounded-lg border border-emerald-200 dark:border-emerald-600 w-full">
                <h4 className="font-bold text-emerald-800 dark:text-emerald-300 text-xs uppercase tracking-wider mb-2">Puntos Fuertes</h4>
                <ul className="list-disc list-inside text-sm text-emerald-800 dark:text-slate-100 space-y-1">
                  {safeArray(reportData.analisis_cv?.puntos_fuertes).map((p, i) => <li key={i}>{formatText(p)}</li>)}
                </ul>
              </div>
              <div className="bg-rose-50/40 dark:bg-slate-900 p-4 rounded-lg border border-rose-200 dark:border-rose-600 w-full">
                <h4 className="font-bold text-rose-800 dark:text-rose-300 text-xs uppercase tracking-wider mb-2">Aspectos a Corregir</h4>
                <ul className="list-disc list-inside text-sm text-rose-800 dark:text-slate-100 space-y-1">
                  {safeArray(reportData.analisis_cv?.aspectos_mejorar).map((p, i) => <li key={i}>{formatText(p)}</li>)}
                </ul>
              </div>
            </div>
          </section>

          <section aria-labelledby="entornos-ideales" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="entornos-ideales" className="text-lg font-bold text-[#374BA6] dark:text-blue-300 pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600">7. Entornos Ideales</h2>
            <ul className="space-y-3 bg-gray-50/80 dark:bg-slate-900 p-5 rounded-lg border border-gray-200 dark:border-slate-600 w-full">
              {safeArray(reportData.entornos_ideales).map((e, idx) => (
                <li key={idx} className="flex gap-3 text-sm text-gray-800 dark:text-slate-100 leading-relaxed text-justify">
                  <span className="text-[#374BA6] dark:text-blue-300 shrink-0 mt-0.5" aria-hidden="true">▪</span> <span>{formatText(e)}</span>
                </li>
              ))}
            </ul>
          </section>

          <section aria-labelledby="roles-recomendados" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="roles-recomendados" className="text-lg font-bold text-[#374BA6] dark:text-blue-300 pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600">8. Roles Recomendados de Transición</h2>
            <div className="flex flex-col space-y-5 w-full">
              {safeArray(reportData.roles_recomendados).map((rol, idx) => (
                <div key={idx} className="bg-white dark:bg-slate-800 border p-5 rounded-lg border-gray-200/80 dark:border-slate-600 shadow-sm w-full">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="text-base font-bold text-gray-800 dark:text-white">{formatText(rol.titulo)}</h3>
                  </div>
                  <div className="flex gap-2 mb-3">
                    <span className="bg-blue-100 dark:bg-blue-200 text-blue-800 dark:text-slate-900 text-[10px] font-bold px-2 py-0.5 rounded">{formatText(rol.nivel)}</span>
                    <span className="bg-purple-100 dark:bg-purple-200 text-purple-800 dark:text-slate-900 text-[10px] font-bold px-2 py-0.5 rounded">{formatText(rol.modalidad)}</span>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-slate-100 text-justify"><strong className="text-gray-900 dark:text-white">Justificación de encaje temporal:</strong> {formatText(rol.por_que_encaja)}</p>
                  <p className="text-[10px] font-bold text-gray-600 dark:text-slate-300 uppercase tracking-wider mt-3">DEMANDA EN MERCADO: {formatText(rol.demanda_laboral)}</p>
                </div>
              ))}
            </div>
          </section>

          <div className="html2pdf__page-break"></div>

          <section aria-labelledby="plan-accion" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="plan-accion" className="text-lg font-bold text-[#374BA6] dark:text-blue-300 pb-2 mb-6 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600">9. Plan de Acción de Capacitación</h2>
            <div className="flex flex-col space-y-6 w-full">
              <div className="bg-white dark:bg-slate-900 border rounded-lg overflow-hidden border-gray-200 dark:border-slate-600 w-full">
                <div className="bg-blue-950 dark:bg-slate-950 text-white px-5 py-3 font-bold uppercase tracking-wider text-sm border-b dark:border-slate-700">Fase 1: Primeros 30 Días</div>
                <ul className="p-5 space-y-3">
                  {safeArray(reportData.plan_accion?.dias_30).map((a, i) => (
                    <li key={i} className="flex gap-3 text-sm text-gray-800 dark:text-slate-100"><span className="text-blue-700 dark:text-blue-300 font-bold shrink-0" aria-hidden="true">✓</span> <span className="text-justify">{formatText(a)}</span></li>
                  ))}
                </ul>
              </div>
              <div className="bg-white dark:bg-slate-900 border rounded-lg overflow-hidden border-gray-200 dark:border-slate-600 w-full">
                <div className="bg-blue-800 dark:bg-slate-950 text-white px-5 py-3 font-bold uppercase tracking-wider text-sm border-b dark:border-slate-700">Fase 2: Días 31 a 60</div>
                <ul className="p-5 space-y-3">
                  {safeArray(reportData.plan_accion?.dias_60).map((a, i) => (
                    <li key={i} className="flex gap-3 text-sm text-gray-800 dark:text-slate-100"><span className="text-blue-600 dark:text-blue-300 font-bold shrink-0" aria-hidden="true">✓</span> <span className="text-justify">{formatText(a)}</span></li>
                  ))}
                </ul>
              </div>
              <div className="bg-white dark:bg-slate-900 border rounded-lg overflow-hidden border-gray-200 dark:border-slate-600 w-full">
                <div className="bg-blue-600 dark:bg-slate-950 text-white px-5 py-3 font-bold uppercase tracking-wider text-sm border-b dark:border-slate-700">Fase 3: Días 61 a 90</div>
                <ul className="p-5 space-y-3">
                  {safeArray(reportData.plan_accion?.dias_90).map((a, i) => (
                    <li key={i} className="flex gap-3 text-sm text-gray-800 dark:text-slate-100"><span className="text-blue-500 dark:text-blue-300 font-bold shrink-0" aria-hidden="true">✓</span> <span className="text-justify">{formatText(a)}</span></li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          <section aria-labelledby="estrategia-busqueda" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="estrategia-busqueda" className="text-lg font-bold text-[#374BA6] dark:text-blue-300 pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600">10. Estrategia de Búsqueda</h2>
            <div className="flex flex-col space-y-3 w-full">
              {safeArray(reportData.estrategia_busqueda).map((est, i) => (
                <div key={i} className="text-sm text-gray-800 dark:text-slate-100 p-4 bg-gray-50 dark:bg-slate-900 border border-gray-200 dark:border-slate-600 rounded-lg text-justify">
                  {formatText(est)}
                </div>
              ))}
            </div>
          </section>

          <section aria-labelledby="herramientas-recomendadas" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="herramientas-recomendadas" className="text-lg font-bold text-[#374BA6] dark:text-blue-300 pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600">11. Herramientas Recomendadas</h2>
            <div className="flex flex-col space-y-3 w-full">
              {safeArray(reportData.herramientas_recomendadas).map((tool, i) => (
                <div key={i} className="flex flex-col bg-white dark:bg-slate-900 border p-4 rounded-lg border-gray-200 dark:border-slate-600 shadow-sm w-full">
                  <span className="text-sm font-bold text-gray-900 dark:text-white mb-1">{formatText(tool.nombre)}</span>
                  <span className="text-sm text-gray-700 dark:text-slate-100 text-justify">{formatText(tool.para_que_sirve)}</span>
                </div>
              ))}
            </div>
          </section>

          <div className="html2pdf__page-break"></div>

          {safeArray(reportData.resultados_juegos).length > 0 && (
            <section aria-labelledby="insights-juegos" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
              <h2 id="insights-juegos" className="text-lg font-bold text-[#374BA6] dark:text-blue-300 pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600">12. Insights de los Minijuegos</h2>
              <div className="flex flex-col space-y-5 w-full">
                {safeArray(reportData.resultados_juegos).map((juego, idx) => (
                  <div key={idx} className="bg-white dark:bg-slate-900 border p-5 rounded-lg border-gray-200 dark:border-slate-600 shadow-sm relative overflow-hidden break-inside-avoid w-full">
                    <div className="absolute top-0 left-0 w-1.5 h-full bg-[#374BA6] dark:bg-blue-400"></div>
                    <h3 className="text-base font-bold text-gray-900 dark:text-white mb-1 pl-2">{formatText(formatGameName(juego.juego))}</h3>
                    <p className="text-[10px] font-bold text-gray-600 dark:text-slate-300 uppercase tracking-wider mb-3 pl-2">DIMENSIÓN: {formatText(juego.que_mide)}</p>
                    <p className="text-sm text-gray-800 dark:text-slate-100 mb-4 leading-relaxed text-justify pl-2"><strong>Mapeo Psicométrico:</strong> {formatText(juego.interpretacion)}</p>
                    <div className="bg-blue-50/50 dark:bg-slate-800 p-4 rounded text-sm text-blue-950 dark:text-slate-100 border border-blue-200/60 dark:border-slate-600 ml-2">
                      <strong className="block mb-1 text-[#374BA6] dark:text-blue-300 font-bold">Transferencia a Entrevista:</strong> <span className="text-justify block">{formatText(juego.aplicacion_entrevista)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          <section aria-labelledby="ajustes-inmediatos" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="ajustes-inmediatos" className="text-lg font-bold text-[#374BA6] dark:text-blue-300 pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600">13. Ajustes Inmediatos</h2>
            <ul className="flex flex-col space-y-3 w-full">
              {safeArray(reportData.recomendaciones_personalizadas).map((rec, i) => (
                <li key={i} className="flex gap-3 text-sm text-gray-800 dark:text-slate-100 bg-gray-50 dark:bg-slate-900 p-4 rounded border border-gray-200 dark:border-slate-600 text-justify">
                  <span className="text-[#374BA6] dark:text-blue-300 font-bold shrink-0 mt-0.5" aria-hidden="true">▪</span> <span>{formatText(rec)}</span>
                </li>
              ))}
            </ul>
          </section>

          <section aria-labelledby="recursos-formativos" className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600">
            <h2 id="recursos-formativos" className="text-lg font-bold text-[#374BA6] dark:text-blue-300 pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600">14. Recursos Formativos Recomendados</h2>
            <div className="flex flex-col space-y-4 w-full">
              {safeArray(reportData.recursos_adicionales).map((rec, i) => (
                <div key={i} className="bg-white dark:bg-slate-900 border p-5 rounded-lg border-gray-200 dark:border-slate-600 shadow-sm w-full">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-bold text-gray-900 dark:text-white">{formatText(rec.nombre)}</span>
                    <span className="text-[10px] font-black uppercase tracking-wider bg-blue-100 dark:bg-blue-200 px-2 py-0.5 rounded text-[#374BA6] dark:text-slate-900 whitespace-nowrap">{formatText(rec.tipo)}</span>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-slate-100 leading-relaxed text-justify">{formatText(rec.descripcion)}</p>
                </div>
              ))}
            </div>
          </section>

          <section aria-labelledby="veredicto" className="break-inside-avoid bg-[#374BA6] dark:bg-slate-950 text-white p-10 rounded-xl text-center shadow border dark:border-slate-700">
            <h2 id="veredicto" className="text-xl font-bold text-blue-200 mb-4 uppercase tracking-widest">Veredicto de Orientación</h2>
            <p className="text-base font-medium leading-relaxed italic max-w-3xl mx-auto text-justify dark:text-slate-100">
              "{formatText(reportData.mensaje_final)}"
            </p>
          </section>

        </main>
      </div>

      {!isExportingPdf && (
        <div className="no-print max-w-[210mm] mx-auto mt-6 bg-white dark:bg-slate-800 p-8 rounded-xl border border-gray-200 dark:border-slate-700 shadow">
          {!feedbackSent ? (
            <form onSubmit={handleFeedbackSubmit} className="max-w-md mx-auto">
              <fieldset className="mb-5 flex flex-col items-center gap-4 w-full">
                <legend className="text-sm font-bold text-center w-full mb-4 text-gray-700 dark:text-white uppercase tracking-widest">Tu Feedback nos ayuda a mejorar</legend>
                <div className="flex justify-center gap-4 w-full">
                  <label className="flex items-center gap-2 cursor-pointer bg-gray-50 dark:bg-slate-900 hover:bg-gray-100 dark:hover:bg-slate-950 px-5 py-3 rounded-lg border border-gray-200 dark:border-slate-600 focus-within:ring-2 focus-within:ring-[#374BA6] transition-colors">
                    <input type="radio" name="rating" value="útil" required onChange={(e) => setFeedback({ ...feedback, rating: e.target.value })} className="w-5 h-5 text-[#374BA6] focus:ring-0 dark:bg-slate-800 border-gray-300 dark:border-slate-500" />
                    <span className="text-sm font-bold text-gray-800 dark:text-slate-100">Informe de alto valor</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer bg-gray-50 dark:bg-slate-900 hover:bg-gray-100 dark:hover:bg-slate-950 px-5 py-3 rounded-lg border border-gray-200 dark:border-slate-600 focus-within:ring-2 focus-within:ring-[#374BA6] transition-colors">
                    <input type="radio" name="rating" value="no útil" required onChange={(e) => setFeedback({ ...feedback, rating: e.target.value })} className="w-5 h-5 text-[#374BA6] focus:ring-0 dark:bg-slate-800 border-gray-300 dark:border-slate-500" />
                    <span className="text-sm font-bold text-gray-800 dark:text-slate-100">Necesita ajustes</span>
                  </label>
                </div>
              </fieldset>
              <textarea 
                placeholder="Indica qué métrica o redacción consideras mejorable..." 
                className="w-full p-4 border border-gray-300 dark:border-slate-500 bg-white dark:bg-slate-900 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-slate-300 rounded-lg mb-4 text-sm focus:ring-2 focus:ring-[#374BA6] focus:outline-none transition-shadow"
                onChange={(e) => setFeedback({ ...feedback, comment: e.target.value })}
                aria-label="Comentarios del analista"
              />
              <div aria-live="polite" className="w-full">
                {feedbackError && <p className="text-sm text-red-700 dark:text-red-300 font-bold mb-3 text-center">{feedbackError}</p>}
              </div>
              <button type="submit" className="w-full bg-gray-900 hover:bg-black dark:bg-blue-600 dark:hover:bg-blue-700 text-white text-sm font-bold py-3 rounded-lg transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-gray-900">
                Enviar Feedback
              </button>
            </form>
          ) : (
            <div className="text-center text-sm text-emerald-800 dark:text-emerald-200 font-bold p-4 bg-emerald-100 dark:bg-slate-900 rounded border border-emerald-200 dark:border-emerald-700" role="status">
              Métrica de feedback enviada correctamente.
            </div>
          )}
          
          <div className="mt-6 pt-6 border-t dark:border-slate-700 text-center">
            {pdfExportError && (
              <div role="alert" aria-live="assertive" className="mb-4 p-3 bg-red-50 dark:bg-slate-800 text-red-700 dark:text-red-300 text-sm font-bold border-l-4 border-red-500 rounded text-left">
                {pdfExportError}
              </div>
            )}

            {isExportingPdf && (
              <div
                role="status"
                aria-live="polite"
                aria-atomic="true"
                className="mb-4 flex items-center justify-center gap-3 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-800 dark:border-blue-700 dark:bg-slate-900 dark:text-blue-200"
              >
                <div className="animate-spin h-4 w-4 border-2 border-blue-700 border-t-transparent rounded-full dark:border-blue-300 dark:border-t-transparent" aria-hidden="true"></div>
                {pdfGenerationMessage}
              </div>
            )}

            <button 
              onClick={handleDownloadPdf} 
              disabled={isExportingPdf}
              aria-busy={isExportingPdf}
              aria-live="polite"
              className="bg-[#374BA6] dark:bg-blue-600 hover:bg-blue-800 dark:hover:bg-blue-700 text-white font-bold py-4 px-10 rounded-lg transition-colors text-base flex items-center justify-center mx-auto gap-3 focus:ring-4 focus:ring-blue-200 disabled:opacity-50"
            >
              {isExportingPdf ? (
                <>
                  <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" aria-hidden="true"></div>
                  Generando PDF...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                  Descargar Informe (PDF)
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}