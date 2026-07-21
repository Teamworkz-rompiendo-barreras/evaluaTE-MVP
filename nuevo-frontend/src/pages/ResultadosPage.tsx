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
import html2pdf from 'html2pdf.js';
import { sendProfileAnalysis } from '../utils/api';
import { useLocation } from 'react-router-dom';

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
  roles_recomendados: Array<{titulo: string, nivel: string, modalidad: string, por_que_encaja: string, salario_orientativo: string, demanda_laboral: string}>;
  plan_accion: {dias_30: string[], dias_60: string[], dias_90: string[]};
  estrategia_busqueda: string[];
  herramientas_recomendadas: Array<{nombre: string, para_que_sirve: string}>;
  resultados_juegos: Array<{juego: string, que_mide: string, resultado: string, interpretacion: string, aplicacion_entrevista: string}>;
  recomendaciones_personalizadas: string[];
  recursos_adicionales: Array<{nombre: string, tipo: string, descripcion: string}>;
  mensaje_final: string;
}

type CvStars = 1 | 2 | 3 | 4 | 5;

const formatText = (text: string) => {
  if (!text) return null;
  const parts = text.split(/(\*\*.*?\*\*)/g);
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

const StarsGold: React.FC<{ n: number }> = ({ n }) => {
  const safeN = Math.max(1, Math.min(5, Math.round(n)));
  const filled = "★".repeat(safeN);
  const empty = "★".repeat(5 - safeN);
  return (
    <span aria-label={`${safeN} de 5 estrellas`}>
      <span className="text-[#374BA6] dark:text-blue-300 font-bold text-lg" aria-hidden="true">{filled}</span>
      <span className="text-gray-300 dark:text-slate-600 opacity-60 text-lg" aria-hidden="true">{empty}</span>
    </span>
  );
};

export default function ResultadosPage() {
  const { user, loading: authLoading } = useAuth();
  const location = useLocation();
  const personal = useAppSelector((state: RootState) => state.personal);
  const game = useAppSelector((state: RootState) => state.game);
  const rawReportFromUpload = location.state?.rawReport;
  
  const initialData = rawReportFromUpload || null;
  
  const [reportData, setReportData] = useState<AdvancedReport | null>(initialData);
  const [loadingIa, setLoadingIa] = useState<boolean>(false);
  const [errorIa, setErrorIa] = useState<string>('');
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [retryCount, setRetryCount] = useState<number>(0);
  
  const reportRef = useRef<HTMLDivElement>(null);
  
  // FIX TÉCNICO (TS2540): Aserción estricta indicando al compilador que es una referencia mutable
  const isFetchingRef = useRef(false) as React.MutableRefObject<boolean>;
  
  const [feedback, setFeedback] = useState<{ rating: string, comment: string }>({ rating: '', comment: '' });
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackError, setFeedbackError] = useState('');
  
  const { rateCv: submitRating } = useCvRating(personal?.report?.userId ?? '', (personal?.report as any)?.id ?? '');

  const asStars = (n: number): CvStars => (n < 1 ? 1 : n > 5 ? 5 : Math.round(n)) as CvStars;

  const softSkillsData = useMemo(() => {
    const allCombinedSkillsMap = new Map();
    [...(personal?.softSkills || []), ...(game?.softSkills || [])].forEach(rawSkill => {
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

  const radarData = useMemo(() => {
    const combined = softSkillsData.map(s => ({ softskill: s.skill as string, score: Number(s.score) || 0 }));
    return processRadarData(combined);
  }, [softSkillsData]);

  const hasAnyRadarValue = radarData.some((item: any) => Number(item?.score) > 0);

  const candidateName = useMemo(() => {
    if (personal?.firstName) {
      return `${personal.firstName} ${personal.lastName || ''}`.trim();
    }
    return reportData?.datos_personales?.['Nombre'] || reportData?.datos_personales?.['nombre'] || 'Candidato';
  }, [personal, reportData]);

  const displayPersonalData = useMemo(() => {
    if (!reportData?.datos_personales) return {};
    
    const { nombre, Nombre, ...restDatos } = reportData.datos_personales;
    
    const merged: Record<string, string> = { 
      'Nombre Completo': candidateName,
      ...restDatos 
    };
    
    return merged;
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
        const formData = new FormData();
        formData.append("game_results", JSON.stringify({ completedGames: game.completedGames, softSkills: softSkillsData }));
        formData.append("preferences", JSON.stringify(personal.jobPreferences || {}));
        
        if (personal.cvAnalysis) {
          formData.append("cv_analysis", JSON.stringify(personal.cvAnalysis));
        }
        
        if (personal.cvFile && personal.cvFile.fileContent) {
          try {
            const fileResponse = await fetch(personal.cvFile.fileContent);
            const blob = await fileResponse.blob();
            formData.append("cv_file", blob, personal.cvFile.fileName || "curriculum.pdf");
          } catch (blobError) {
            console.error("Fallo al reconstruir el archivo físico desde memoria local:", blobError);
          }
        }
        
        formData.append("contact_info", JSON.stringify({
          firstName: personal.firstName,
          lastName: personal.lastName,
          email: personal.email
        }));

        const data = await sendProfileAnalysis(formData, user?.id || "anonymous-guest-123");
        
        if (data && typeof data === 'object') {
          setReportData(data as AdvancedReport);
        } else {
          setErrorIa('La respuesta del servidor no tiene el formato esperado.');
        }
      } catch (err: any) {
        let safeErrorMsg = 'Los servidores de análisis están experimentando alta demanda. Por favor, reinténtalo en un momento.';
        if (err && typeof err.message === 'string') {
          safeErrorMsg = err.message;
        } else if (err && typeof err.message === 'object') {
          safeErrorMsg = JSON.stringify(err.message);
        } else if (typeof err === 'string') {
          safeErrorMsg = err;
        }
        setErrorIa(safeErrorMsg);
      } finally {
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
    window.scrollTo(0, 0);
    await new Promise((resolve) => setTimeout(resolve, 400)); 
    
    const htmlEl = document.documentElement;
    const wasDark = htmlEl.classList.contains('dark');
    if (wasDark) htmlEl.classList.remove('dark');
    
    try {
      const pdfOptions: any = {
        margin: [12, 12, 12, 12],
        filename: `Informe_B2B_${candidateName.replace(/\s+/g, '_')}.pdf`,
        image: { type: 'jpeg', quality: 1.0 },
        html2canvas: { scale: 2, useCORS: true, backgroundColor: '#ffffff', windowWidth: 1100 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak: { mode: ['css', 'legacy'], avoid: ['.break-inside-avoid'] }
      };

      await html2pdf().set(pdfOptions).from(element).save();
    } finally {
      if (wasDark) htmlEl.classList.add('dark');
      setIsExportingPdf(false);
    }
  };

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedbackError('');
    try {
      const backendUrl = 'http://localhost:8080/api/informe-ia/feedback';
      const res = await fetch(backendUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ informe: reportData?.resumen_ejecutivo || "N/A", rating: feedback.rating, comment: feedback.comment })
      });
      if (res.ok) {
        setFeedbackSent(true);
      } else {
        setFeedbackError('No se pudo registrar la valoración en el servidor.');
      }
    } catch { 
      setFeedbackError('Error de red. Verifica que el servidor Backend (puerto 8080) esté activo.'); 
    }
  };

  if (loadingIa && !reportData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-slate-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-[#374BA6] dark:border-blue-400"></div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mt-4" aria-live="polite">Analizando variables y construyendo informe puente...</h2>
      </div>
    );
  }

  if (errorIa && !reportData) {
    return (
      <div className="max-w-2xl mx-auto mt-20 bg-red-50 dark:bg-slate-800 border-l-4 border-red-500 dark:border-red-400 p-6 rounded shadow-lg" role="alert" aria-live="assertive">
        <h3 className="text-lg font-bold text-red-800 dark:text-red-200 mb-2">Aviso de Disponibilidad</h3>
        <p className="text-red-700 dark:text-slate-100 mb-4 break-words">{errorIa}</p>
        <button 
          onClick={() => {
            isFetchingRef.current = false;
            setRetryCount(prev => prev + 1);
          }} 
          className="bg-red-700 hover:bg-red-800 dark:bg-red-600 dark:hover:bg-red-500 text-white font-bold py-2 px-6 rounded transition"
        >
          Reintentar Proceso
        </button>
      </div>
    );
  }

  if (!reportData) return null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 py-8 font-sans text-gray-900 dark:text-slate-50 print:bg-white print:py-0">
      <div ref={reportRef} className="max-w-[210mm] mx-auto bg-white dark:bg-slate-800 print:shadow-none shadow-xl border border-gray-200/60 dark:border-slate-700 overflow-hidden w-full print:border-gray-200">
        
        {/* SECCIÓN 0: PORTADA EDITORIAL */}
        <div className="bg-[#374BA6] dark:bg-slate-950 text-white p-16 flex flex-col items-center justify-center text-center relative print:bg-[#374BA6] print:h-[290mm]">
          <img src={logo} alt="Teamworkz" className="h-16 mb-12 brightness-0 invert" aria-hidden="true" />
          <h1 className="text-5xl font-black tracking-tight mb-6 leading-tight text-white dark:text-white">Informe Profesional<br/>de Empleabilidad</h1>
          <h2 className="text-md uppercase tracking-[0.4em] font-bold text-blue-200 dark:text-blue-200 print:text-blue-200 mb-4">EvalúaTE</h2>
          <p className="text-lg text-blue-100 dark:text-slate-200 print:text-blue-100 font-medium mb-20">Consultoría de Talento Corporativo y Estrategia Laboral</p>
          
          <div className="bg-white/10 dark:bg-slate-800/80 backdrop-blur-md px-12 py-6 rounded-xl border border-white/10 dark:border-slate-600 print:bg-white/10 print:border-white/10 w-full max-w-md">
            <p className="text-sm text-blue-200 dark:text-blue-200 print:text-blue-200 font-semibold mb-1">{new Date().toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
            <h2 className="text-3xl font-bold tracking-tight text-white dark:text-white">{candidateName}</h2>
          </div>
        </div>
        
        <div className="html2pdf__page-break"></div>

        {/* CONTENIDO DICTATORIAL VERTICAL */}
        <div className="p-12 space-y-12 print:p-10">
          
          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <div className="flex flex-col items-center bg-gray-50 dark:bg-slate-900 print:bg-gray-50 rounded-xl p-8 border border-gray-200/50 dark:border-slate-600 print:border-gray-200/50">
                <span className="text-xs font-bold uppercase tracking-wider text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] block mb-2">ÍNDICE GLOBAL</span>
                <div className="text-6xl font-black text-gray-900 dark:text-white print:text-gray-900 tabular-nums mb-4">{reportData.puntuacion_global}<span className="text-2xl text-gray-400 dark:text-slate-300 print:text-gray-400 font-normal" aria-hidden="true">/100</span></div>
                <p className="text-gray-700 dark:text-slate-100 print:text-gray-700 leading-relaxed font-semibold text-sm text-justify">
                  {formatText(reportData.interpretacion_global)}
                </p>
            </div>
          </section>

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/10 dark:border-slate-600 print:border-[#374BA6]/10">1. Resumen Ejecutivo</h2>
            <p className="text-sm leading-relaxed text-gray-700 dark:text-slate-100 print:text-gray-700 text-justify font-medium">
              {formatText(reportData.resumen_ejecutivo)}
            </p>
          </section>

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/10 dark:border-slate-600 print:border-[#374BA6]/10">2. Perfil Personal</h2>
            <div className="flex flex-wrap gap-4">
              {Object.entries(displayPersonalData).map(([key, value]) => (
                <div key={key} className="flex-1 min-w-[150px] bg-gray-50/80 dark:bg-slate-900 print:bg-gray-50/80 p-3 rounded border border-gray-100 dark:border-slate-600 print:border-gray-100">
                  <p className="text-[10px] font-bold text-gray-400 dark:text-slate-200 print:text-gray-400 uppercase tracking-widest mb-0.5">{key}</p>
                  <p className="text-xs font-bold text-gray-900 dark:text-white print:text-gray-900 truncate" title={String(value)}>{String(value) || '-'}</p>
                </div>
              ))}
            </div>
          </section>

          <div className="html2pdf__page-break"></div>

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] pb-2 mb-6 uppercase tracking-wider border-b border-[#374BA6]/10 dark:border-slate-600 print:border-[#374BA6]/10">3. Perfil de Competencias</h2>
            
            <div style={{ width: '600px', height: '480px', margin: '0 auto', display: 'block', position: 'relative' }} className="nivo-radar-wrapper bg-white dark:bg-slate-900 print:bg-white mb-8 border border-gray-50 dark:border-slate-600 print:border-gray-50 rounded-xl" aria-hidden="true">
              <style dangerouslySetInnerHTML={{__html: `
                .dark .nivo-radar-wrapper text { fill: #ffffff !important; font-weight: 700 !important; font-size: 11px !important; }
                .dark .nivo-radar-wrapper line,
                .dark .nivo-radar-wrapper path[stroke-dasharray] { stroke: #64748b !important; }
                .dark .nivo-radar-wrapper path:not([stroke-dasharray]) { fill: #3b82f6 !important; fill-opacity: 0.4 !important; stroke: #93c5fd !important; stroke-width: 2px !important; }
                .dark .nivo-radar-wrapper circle { fill: #0f172a !important; stroke: #93c5fd !important; stroke-width: 2px !important; r: 4 !important; }
              `}} />
              {hasAnyRadarValue ? (
                <ResponsiveRadar
                  data={radarData as unknown as Array<Record<string, unknown>>}
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
                <p className="text-gray-400 dark:text-slate-200 italic text-xs text-center mt-20">Datos de competencias no disponibles para graficar.</p>
              )}
            </div>

            <div className="flex flex-col space-y-8 mt-6 w-full">
              {(reportData.perfil_competencias || []).map((grupo, idx) => (
                <div key={idx} className="break-inside-avoid w-full">
                  <h3 className="text-xs font-bold text-gray-400 dark:text-slate-200 print:text-gray-400 uppercase tracking-widest mb-4 border-l-4 border-[#374BA6] dark:border-blue-400 print:border-[#374BA6] pl-2 bg-gray-50/50 dark:bg-slate-900 print:bg-gray-50/50 py-1.5">{grupo.categoria}</h3>
                  <div className="flex flex-col space-y-5 w-full">
                    {(grupo.competencias || []).map((comp, cIdx) => (
                      <div key={cIdx} className="border-b border-gray-50 dark:border-slate-700 print:border-gray-50 pb-3 last:border-0 w-full">
                        <div className="flex justify-between items-end mb-1">
                          <span className="text-sm font-bold text-gray-800 dark:text-white print:text-gray-800">{comp.nombre}</span>
                          <span className="text-[10px] font-black text-[#374BA6] dark:text-slate-900 print:text-[#374BA6] bg-blue-50 dark:bg-blue-200 print:bg-blue-50 px-2 py-0.5 rounded">{comp.puntuacion}/100</span>
                        </div>
                        <div className="w-full bg-gray-100 dark:bg-slate-700 print:bg-gray-100 rounded-full h-1.5 mb-2" aria-hidden="true">
                          <div className="bg-[#374BA6] dark:bg-blue-400 print:bg-[#374BA6] h-1.5 rounded-full" style={{ width: `${comp.puntuacion}%` }}></div>
                        </div>
                        <p className="text-xs text-gray-600 dark:text-slate-100 print:text-gray-600 leading-relaxed text-justify">{formatText(comp.explicacion)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>

          <div className="html2pdf__page-break"></div>

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-emerald-700 dark:text-emerald-300 print:text-emerald-700 pb-2 mb-4 uppercase tracking-wider border-b border-emerald-100 dark:border-slate-600 print:border-emerald-100">4. Fortalezas Principales</h2>
            <div className="flex flex-col space-y-4 w-full">
              {(reportData.fortalezas_principales || []).map((f, idx) => (
                <div key={idx} className="bg-emerald-50/40 dark:bg-slate-900 print:bg-emerald-50/40 p-5 rounded-lg border-l-4 border-emerald-500 dark:border-emerald-400 print:border-emerald-500 w-full">
                  <h3 className="text-sm font-bold text-emerald-900 dark:text-emerald-200 print:text-emerald-900 mb-2 uppercase tracking-wider">{formatText(f.nombre)}</h3>
                  <p className="text-xs text-emerald-800 dark:text-slate-100 print:text-emerald-800 leading-relaxed text-justify">{formatText(f.explicacion_practica)}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-amber-600 dark:text-amber-300 print:text-amber-600 pb-2 mb-4 uppercase tracking-wider border-b border-amber-100 dark:border-slate-600 print:border-amber-100">5. Áreas de Mejora</h2>
            <div className="flex flex-col space-y-4 w-full">
              {(reportData.areas_mejora || []).map((m, idx) => (
                <div key={idx} className="bg-amber-50/30 dark:bg-slate-900 print:bg-amber-50/30 p-5 rounded-lg border-l-4 border-amber-500 dark:border-amber-400 print:border-amber-500 w-full">
                  <h3 className="text-sm font-bold text-amber-900 dark:text-amber-200 print:text-amber-900 mb-2 uppercase tracking-wider">{formatText(m.nombre)}</h3>
                  <p className="text-xs text-amber-800 dark:text-slate-100 print:text-amber-800 mb-3 text-justify">{formatText(m.porque_afecta)}</p>
                  <div className="mt-3 pt-3 border-t border-amber-200/50 dark:border-amber-700/50 print:border-amber-200/50">
                    <p className="text-[10px] font-bold text-amber-900 dark:text-amber-200 print:text-amber-900 uppercase tracking-widest mb-2">Plan de capacitación inmediata:</p>
                    <ul className="list-disc list-inside text-xs text-amber-800 dark:text-slate-100 print:text-amber-800 space-y-1.5">
                      {(m.acciones_concretas || []).map((acc, aIdx) => <li key={aIdx} className="text-justify">{formatText(acc)}</li>)}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <div className="html2pdf__page-break"></div>

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] pb-2 mb-6 uppercase tracking-wider border-b border-[#374BA6]/10 dark:border-slate-600 print:border-[#374BA6]/10">6. Análisis Profesional del CV</h2>
            
            <div className="flex flex-col items-center gap-4 mb-8 bg-gray-50 dark:bg-slate-900 print:bg-gray-50 p-6 rounded-xl border border-gray-100 dark:border-slate-600 print:border-gray-100 w-full">
              <div className="flex flex-col items-center justify-center w-full max-w-[200px] bg-white dark:bg-slate-800 print:bg-white p-4 rounded-lg border border-gray-200/60 dark:border-slate-600 print:border-gray-200/60">
                <span className="text-[10px] font-bold text-gray-400 dark:text-slate-300 print:text-gray-400 uppercase tracking-widest text-center">ATS MATCH</span>
                <div className="text-4xl font-black text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] my-1">{reportData.analisis_cv?.ats_compatibilidad}%</div>
                <div className="w-full bg-gray-200 dark:bg-slate-700 print:bg-gray-200 rounded-full h-1.5" aria-hidden="true">
                  <div className="h-1.5 rounded-full bg-[#374BA6] dark:bg-blue-400 print:bg-[#374BA6]" style={{ width: `${reportData.analisis_cv?.ats_compatibilidad || 0}%` }}></div>
                </div>
              </div>
              <p className="text-sm text-gray-700 dark:text-slate-100 print:text-gray-700 italic border-l-4 border-gray-300 dark:border-slate-500 print:border-gray-300 pl-4 text-justify mt-2">"{formatText(reportData.analisis_cv?.resumen)}"</p>
            </div>

            <div className="flex flex-col space-y-6 w-full">
              <div>
                <h3 className="font-bold text-gray-400 dark:text-slate-200 print:text-gray-400 uppercase text-xs tracking-wider mb-3">Métricas de Documentación</h3>
                <ul className="space-y-2 bg-gray-50/50 dark:bg-slate-900 print:bg-gray-50/50 p-4 rounded-lg border dark:border-slate-600 print:border-gray-100">
                  <li className="flex justify-between items-center border-b border-gray-100 dark:border-slate-700 print:border-gray-100 pb-2">
                    <span className="text-sm font-semibold text-gray-600 dark:text-slate-100 print:text-gray-600">Formato Estructural</span> <StarsGold n={reportData.analisis_cv?.valoraciones?.formato || 0} />
                  </li>
                  <li className="flex justify-between items-center border-b border-gray-100 dark:border-slate-700 print:border-gray-100 pb-2">
                    <span className="text-sm font-semibold text-gray-600 dark:text-slate-100 print:text-gray-600">Claridad Narrativa</span> <StarsGold n={reportData.analisis_cv?.valoraciones?.claridad || 0} />
                  </li>
                  <li className="flex justify-between items-center border-b border-gray-100 dark:border-slate-700 print:border-gray-100 pb-2">
                    <span className="text-sm font-semibold text-gray-600 dark:text-slate-100 print:text-gray-600">Coherencia de Trayectoria</span> <StarsGold n={reportData.analisis_cv?.valoraciones?.coherencia || 0} />
                  </li>
                  <li className="flex justify-between items-center border-b border-gray-100 dark:border-slate-700 print:border-gray-100 pb-2">
                    <span className="text-sm font-semibold text-gray-600 dark:text-slate-100 print:text-gray-600">Información de Impacto Clave</span> <StarsGold n={reportData.analisis_cv?.valoraciones?.info_clave || 0} />
                  </li>
                  <li className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-gray-600 dark:text-slate-100 print:text-gray-600">Léxico y Ortografía</span> <StarsGold n={reportData.analisis_cv?.valoraciones?.ortografia || 0} />
                  </li>
                </ul>
              </div>
              
              <div className="bg-emerald-50/40 dark:bg-slate-900 print:bg-emerald-50/40 p-4 rounded-lg border border-emerald-100 dark:border-emerald-600 print:border-emerald-100 w-full">
                <h4 className="font-bold text-emerald-800 dark:text-emerald-300 print:text-emerald-800 text-xs uppercase tracking-wider mb-2">Puntos Fuertes</h4>
                <ul className="list-disc list-inside text-sm text-emerald-700 dark:text-slate-100 print:text-emerald-700 space-y-1">
                  {(reportData.analisis_cv?.puntos_fuertes || []).map((p, i) => <li key={i}>{formatText(p)}</li>)}
                </ul>
              </div>
              <div className="bg-rose-50/40 dark:bg-slate-900 print:bg-rose-50/40 p-4 rounded-lg border border-rose-100 dark:border-rose-600 print:border-rose-100 w-full">
                <h4 className="font-bold text-rose-800 dark:text-rose-300 print:text-rose-800 text-xs uppercase tracking-wider mb-2">Aspectos a Corregir</h4>
                <ul className="list-disc list-inside text-sm text-rose-700 dark:text-slate-100 print:text-rose-700 space-y-1">
                  {(reportData.analisis_cv?.aspectos_mejorar || []).map((p, i) => <li key={i}>{formatText(p)}</li>)}
                </ul>
              </div>
            </div>
          </section>

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600 print:border-[#374BA6]/20">7. Entornos Ideales</h2>
            <ul className="space-y-3 bg-gray-50/80 dark:bg-slate-900 print:bg-gray-50/80 p-5 rounded-lg border dark:border-slate-600 print:border-gray-200 w-full">
              {(reportData.entornos_ideales || []).map((e, idx) => (
                <li key={idx} className="flex gap-3 text-sm text-gray-700 dark:text-slate-100 print:text-gray-700 leading-relaxed text-justify">
                  <span className="text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] shrink-0 mt-0.5" aria-hidden="true">▪</span> <span>{formatText(e)}</span>
                </li>
              ))}
            </ul>
          </section>

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600 print:border-[#374BA6]/20">8. Roles Recomendados de Transición</h2>
            <div className="flex flex-col space-y-5 w-full">
              {(reportData.roles_recomendados || []).map((rol, idx) => (
                <div key={idx} className="bg-white dark:bg-slate-800 print:bg-white border p-5 rounded-lg border-gray-200/80 dark:border-slate-600 print:border-gray-200/80 shadow-sm w-full">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="text-base font-bold text-gray-800 dark:text-white print:text-gray-800">{formatText(rol.titulo)}</h3>
                    <span className="text-sm font-black text-emerald-600 dark:text-slate-900 print:text-emerald-600 bg-emerald-50 dark:bg-emerald-200 print:bg-emerald-50 px-3 py-1 rounded">{rol.salario_orientativo}</span>
                  </div>
                  <div className="flex gap-2 mb-3">
                    <span className="bg-blue-50 dark:bg-blue-200 text-blue-700 dark:text-slate-900 print:bg-blue-50 print:text-blue-700 text-[10px] font-bold px-2 py-0.5 rounded">{rol.nivel}</span>
                    <span className="bg-purple-50 dark:bg-purple-200 text-purple-700 dark:text-slate-900 print:bg-purple-50 print:text-purple-700 text-[10px] font-bold px-2 py-0.5 rounded">{rol.modalidad}</span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-slate-100 print:text-gray-600 text-justify"><strong className="text-gray-900 dark:text-white">Justificación de encaje temporal:</strong> {formatText(rol.por_que_encaja)}</p>
                  <p className="text-[10px] font-bold text-gray-400 dark:text-slate-300 print:text-gray-400 uppercase tracking-wider mt-3">Demanda en Mercado: {rol.demanda_laboral}</p>
                </div>
              ))}
            </div>
          </section>

          <div className="html2pdf__page-break"></div>

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] pb-2 mb-6 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600 print:border-[#374BA6]/20">9. Plan de Acción de Capacitación</h2>
            <div className="flex flex-col space-y-6 w-full">
              <div className="bg-white dark:bg-slate-900 print:bg-white border rounded-lg overflow-hidden border-gray-200 dark:border-slate-600 print:border-gray-200 w-full">
                <div className="bg-blue-950 dark:bg-slate-950 print:bg-blue-950 text-white px-5 py-3 font-bold uppercase tracking-wider text-sm border-b dark:border-slate-700">Fase 1: Primeros 30 Días</div>
                <ul className="p-5 space-y-3">
                  {(reportData.plan_accion?.dias_30 || []).map((a, i) => (
                    <li key={i} className="flex gap-3 text-sm text-gray-700 dark:text-slate-100 print:text-gray-700"><span className="text-blue-600 dark:text-blue-300 print:text-blue-600 font-bold shrink-0" aria-hidden="true">✓</span> <span className="text-justify">{formatText(a)}</span></li>
                  ))}
                </ul>
              </div>
              <div className="bg-white dark:bg-slate-900 print:bg-white border rounded-lg overflow-hidden border-gray-200 dark:border-slate-600 print:border-gray-200 w-full">
                <div className="bg-blue-800 dark:bg-slate-950 print:bg-blue-800 text-white px-5 py-3 font-bold uppercase tracking-wider text-sm border-b dark:border-slate-700">Fase 2: Días 31 a 60</div>
                <ul className="p-5 space-y-3">
                  {(reportData.plan_accion?.dias_60 || []).map((a, i) => (
                    <li key={i} className="flex gap-3 text-sm text-gray-700 dark:text-slate-100 print:text-gray-700"><span className="text-blue-500 dark:text-blue-300 print:text-blue-500 font-bold shrink-0" aria-hidden="true">✓</span> <span className="text-justify">{formatText(a)}</span></li>
                  ))}
                </ul>
              </div>
              <div className="bg-white dark:bg-slate-900 print:bg-white border rounded-lg overflow-hidden border-gray-200 dark:border-slate-600 print:border-gray-200 w-full">
                <div className="bg-blue-600 dark:bg-slate-950 print:bg-blue-600 text-white px-5 py-3 font-bold uppercase tracking-wider text-sm border-b dark:border-slate-700">Fase 3: Días 61 a 90</div>
                <ul className="p-5 space-y-3">
                  {(reportData.plan_accion?.dias_90 || []).map((a, i) => (
                    <li key={i} className="flex gap-3 text-sm text-gray-700 dark:text-slate-100 print:text-gray-700"><span className="text-blue-400 dark:text-blue-300 print:text-blue-400 font-bold shrink-0" aria-hidden="true">✓</span> <span className="text-justify">{formatText(a)}</span></li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600 print:border-[#374BA6]/20">10. Estrategia de Búsqueda</h2>
            <div className="flex flex-col space-y-3 w-full">
              {(reportData.estrategia_busqueda || []).map((est, i) => (
                <div key={i} className="text-sm text-gray-700 dark:text-slate-100 print:text-gray-700 p-4 bg-gray-50 dark:bg-slate-900 print:bg-gray-50 border border-gray-100 dark:border-slate-600 print:border-gray-100 rounded-lg text-justify">
                  {formatText(est)}
                </div>
              ))}
            </div>
          </section>

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600 print:border-[#374BA6]/20">11. Herramientas Recomendadas</h2>
            <div className="flex flex-col space-y-3 w-full">
              {(reportData.herramientas_recomendadas || []).map((tool, i) => (
                <div key={i} className="flex flex-col bg-white dark:bg-slate-900 print:bg-white border p-4 rounded-lg border-gray-100 dark:border-slate-600 print:border-gray-100 shadow-sm w-full">
                  <span className="text-sm font-bold text-gray-900 dark:text-white print:text-gray-900 mb-1">{formatText(tool.nombre)}</span>
                  <span className="text-sm text-gray-600 dark:text-slate-100 print:text-gray-600 text-justify">{formatText(tool.para_que_sirve)}</span>
                </div>
              ))}
            </div>
          </section>

          <div className="html2pdf__page-break"></div>

          {(reportData.resultados_juegos || []).length > 0 && (
            <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
              <h2 className="text-lg font-bold text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600 print:border-[#374BA6]/20">12. Insights de los Minijuegos</h2>
              <div className="flex flex-col space-y-5 w-full">
                {reportData.resultados_juegos.map((juego, idx) => (
                  <div key={idx} className="bg-white dark:bg-slate-900 print:bg-white border p-5 rounded-lg border-gray-200 dark:border-slate-600 print:border-gray-200 shadow-sm relative overflow-hidden break-inside-avoid w-full">
                    <div className="absolute top-0 left-0 w-1.5 h-full bg-[#374BA6] dark:bg-blue-400 print:bg-[#374BA6]"></div>
                    <h3 className="text-base font-bold text-gray-900 dark:text-white print:text-gray-900 mb-1 pl-2">{formatText(juego.juego)}</h3>
                    <p className="text-[10px] font-bold text-gray-400 dark:text-slate-300 print:text-gray-400 uppercase tracking-wider mb-3 pl-2">Dimensión: {formatText(juego.que_mide)}</p>
                    <p className="text-sm text-gray-700 dark:text-slate-100 print:text-gray-700 mb-4 leading-relaxed text-justify pl-2"><strong>Mapeo Psicométrico:</strong> {formatText(juego.interpretacion)}</p>
                    <div className="bg-blue-50/50 dark:bg-slate-800 print:bg-blue-50/50 p-4 rounded text-sm text-blue-950 dark:text-slate-100 print:text-blue-950 border border-blue-100/60 dark:border-slate-600 print:border-blue-100/60 ml-2">
                      <strong className="block mb-1 text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] font-bold">Transferencia a Entrevista:</strong> <span className="text-justify block">{formatText(juego.aplicacion_entrevista)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600 print:border-[#374BA6]/20">13. Ajustes Inmediatos</h2>
            <ul className="flex flex-col space-y-3 w-full">
              {(reportData.recomendaciones_personalizadas || []).map((rec, i) => (
                <li key={i} className="flex gap-3 text-sm text-gray-700 dark:text-slate-100 print:text-gray-700 bg-gray-50 dark:bg-slate-900 print:bg-gray-50 p-4 rounded border border-gray-100 dark:border-slate-600 print:border-gray-100 text-justify">
                  <span className="text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] font-bold shrink-0 mt-0.5" aria-hidden="true">▪</span> <span>{formatText(rec)}</span>
                </li>
              ))}
            </ul>
          </section>

          <section className="break-inside-avoid border-b pb-8 border-gray-100 dark:border-slate-600 print:border-gray-100">
            <h2 className="text-lg font-bold text-[#374BA6] dark:text-blue-300 print:text-[#374BA6] pb-2 mb-4 uppercase tracking-wider border-b border-[#374BA6]/20 dark:border-slate-600 print:border-[#374BA6]/20">14. Recursos Formativos Recomendados</h2>
            <div className="flex flex-col space-y-4 w-full">
              {(reportData.recursos_adicionales || []).map((rec, i) => (
                <div key={i} className="bg-white dark:bg-slate-900 print:bg-white border p-5 rounded-lg border-gray-100 dark:border-slate-600 print:border-gray-100 shadow-sm w-full">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-bold text-gray-900 dark:text-white print:text-gray-900">{formatText(rec.nombre)}</span>
                    <span className="text-[10px] font-black uppercase tracking-wider bg-blue-50 dark:bg-blue-200 print:bg-blue-50 px-2 py-0.5 rounded text-[#374BA6] dark:text-slate-900 print:text-[#374BA6] whitespace-nowrap">{rec.tipo}</span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-slate-100 print:text-gray-600 leading-relaxed text-justify">{formatText(rec.descripcion)}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="break-inside-avoid bg-[#374BA6] dark:bg-slate-950 print:bg-[#374BA6] text-white p-10 rounded-xl text-center shadow border dark:border-slate-700 print:border-none">
            <h2 className="text-xl font-bold text-blue-200 dark:text-blue-100 print:text-blue-200 mb-4 uppercase tracking-widest">Veredicto de Orientación</h2>
            <p className="text-base font-medium leading-relaxed italic max-w-3xl mx-auto text-justify dark:text-slate-100">
              "{formatText(reportData.mensaje_final)}"
            </p>
          </section>

        </div>
      </div>

      {!isExportingPdf && (
        <div className="max-w-[210mm] mx-auto mt-6 bg-white dark:bg-slate-800 p-8 rounded-xl border border-gray-200 dark:border-slate-700 shadow print:hidden">
          {!feedbackSent ? (
            <form onSubmit={handleFeedbackSubmit} className="max-w-md mx-auto">
              <fieldset className="mb-5 flex flex-col items-center gap-4 w-full">
                <legend className="text-sm font-bold text-center w-full mb-4 text-gray-500 dark:text-white uppercase tracking-widest">Tu Feedback nos ayuda a mejorar</legend>
                <div className="flex justify-center gap-4 w-full">
                  <label className="flex items-center gap-2 cursor-pointer bg-gray-50 dark:bg-slate-900 hover:bg-gray-100 dark:hover:bg-slate-950 px-5 py-3 rounded-lg border dark:border-slate-600 focus-within:ring-2 focus-within:ring-[#374BA6] dark:focus-within:ring-blue-400 transition-colors">
                    <input type="radio" name="rating" value="útil" required onChange={(e) => setFeedback({ ...feedback, rating: e.target.value })} className="w-5 h-5 text-[#374BA6] dark:text-blue-400 focus:ring-0 dark:bg-slate-800 border-gray-300 dark:border-slate-500" />
                    <span className="text-sm font-bold text-gray-700 dark:text-slate-100">Informe de alto valor</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer bg-gray-50 dark:bg-slate-900 hover:bg-gray-100 dark:hover:bg-slate-950 px-5 py-3 rounded-lg border dark:border-slate-600 focus-within:ring-2 focus-within:ring-[#374BA6] dark:focus-within:ring-blue-400 transition-colors">
                    <input type="radio" name="rating" value="no útil" required onChange={(e) => setFeedback({ ...feedback, rating: e.target.value })} className="w-5 h-5 text-[#374BA6] dark:text-blue-400 focus:ring-0 dark:bg-slate-800 border-gray-300 dark:border-slate-500" />
                    <span className="text-sm font-bold text-gray-700 dark:text-slate-100">Necesita ajustes</span>
                  </label>
                </div>
              </fieldset>
              <textarea 
                placeholder="Indica qué métrica o redacción consideras mejorable..." 
                className="w-full p-4 border dark:border-slate-500 bg-white dark:bg-slate-900 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-300 rounded-lg mb-4 text-sm focus:ring-2 focus:ring-[#374BA6] dark:focus:ring-blue-400 focus:outline-none transition-shadow"
                onChange={(e) => setFeedback({ ...feedback, comment: e.target.value })}
                aria-label="Comentarios del analista"
              />
              <div aria-live="polite" className="w-full">
                {feedbackError && <p className="text-sm text-red-600 dark:text-red-300 font-bold mb-3 text-center">{feedbackError}</p>}
              </div>
              <button type="submit" className="w-full bg-gray-900 hover:bg-black dark:bg-blue-600 dark:hover:bg-blue-700 text-white text-sm font-bold py-3 rounded-lg transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-gray-900 dark:focus:ring-offset-slate-800">
                Registrar Evaluación Técnico-Económica
              </button>
            </form>
          ) : (
            <div className="text-center text-sm text-emerald-600 dark:text-emerald-200 font-bold p-4 bg-emerald-50 dark:bg-slate-900 rounded border border-emerald-200 dark:border-emerald-700" role="status">
              Métrica de feedback enviada correctamente.
            </div>
          )}
          
          <div className="mt-6 pt-6 border-t dark:border-slate-700 text-center">
            <button onClick={handleDownloadPdf} className="bg-[#374BA6] dark:bg-blue-600 hover:bg-blue-800 dark:hover:bg-blue-700 text-white font-bold py-4 px-10 rounded-lg transition-colors text-base flex items-center justify-center mx-auto gap-3 focus:ring-4 focus:ring-blue-200 dark:focus:ring-blue-900">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
              Exportar Informe Comercial (A4 PDF)
            </button>
          </div>
        </div>
      )}
    </div>
  );
}