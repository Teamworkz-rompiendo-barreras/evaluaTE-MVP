// src/pages/ResultadosPage.tsx
import React, { useEffect, useState } from 'react';
import { useAppSelector } from '../app/hooks';
import type { RootState } from '../app/store';
import { buildApiUrl, API_CONFIG } from '../config/api';
import { ResponsiveRadar } from '@nivo/radar';
import logo from '../assets/Logo_teamworkz.png';
import ReactMarkdown from 'react-markdown';
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


// Función más robusta para manejar datos anidados de recomendaciones
function safeGetRecommendations(data: unknown, path: string): unknown[] {
  try {
    console.log(`🔍 DEBUG - safeGetRecommendations llamada con path: ${path}`);
    console.log(`🔍 DEBUG - data:`, data);
    
    if (!data || typeof data !== 'object') {
      console.log(`🔍 DEBUG - data no es objeto, retornando []`);
      return [];
    }
    
    const keys = path.split('.');
    let current = data as Record<string, unknown>;
    
    for (const key of keys) {
      console.log(`🔍 DEBUG - Navegando clave: ${key}, current:`, current);
      if (current && typeof current === 'object' && key in current) {
        current = current[key] as Record<string, unknown>;
      } else {
        console.log(`🔍 DEBUG - Clave ${key} no encontrada, retornando []`);
        return [];
      }
    }
    
    const result = Array.isArray(current) ? current : [];
    console.log(`🔍 DEBUG - Resultado final para ${path}:`, result);
    return result;
  } catch (error) {
    console.warn(`Error accessing path ${path}:`, error);
    return [];
  }
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
  const [loadingIa, setLoadingIa] = useState<boolean>(false);
  const [errorIa, setErrorIa] = useState<string>('');

  // Llamar al endpoint de IA al cargar la página
  useEffect(() => {
    const fetchIaReport = async () => {
      setLoadingIa(true);
      setErrorIa('');
      
      try {
        const requestBody = {
          userId: report?.userId || 'user',
          fullName: `${report?.firstName || ''} ${report?.lastName || ''}`.trim() || 'Usuario',
          softSkills: filterValidSoftSkills(personal.softSkills || []).map((skill) => ({
            skill: skill.skill,
            score: skill.score,
            level: typeof skill.level === 'string' ? skill.level.charAt(0).toUpperCase() + skill.level.slice(1) : 'Bajo',
            confidence: skill.confidence,
          })),
          cvAnalysis: cvAnalysis ? {
            strengths: cvAnalysis.strengths ?? [],
            weaknesses: cvAnalysis.weaknesses ?? [],
            feedback: cvAnalysis.feedback ?? '',
            structure: cvAnalysis.structure ?? 'regular',
            coherence: cvAnalysis.coherence ?? 'regular',
            experience: cvAnalysis.experience ?? 'regular',
            skills: cvAnalysis.skills ?? [],
            education: cvAnalysis.education ?? [],
            alerts: cvAnalysis.alerts ?? [],
          } : null,
          jobPreferences: report?.jobPreferences || null,
          completedGames: game?.completedGames || [],
          logs: []
        };

        const res = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.IA_REPORT), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody),
          signal: AbortSignal.timeout(120000), // Timeout de 2 minutos
        });
        const data = await res.json();
        console.log('🔍 DEBUG - Respuesta del backend:', data);
        console.log('🔍 DEBUG - res.ok:', res.ok);
        console.log('🔍 DEBUG - data exists:', !!data);
        console.log('🔍 DEBUG - data.summary exists:', !!data?.summary);
        console.log('🔍 DEBUG - data.summary value:', data?.summary);
        console.log('🔍 DEBUG - data.recommendations exists:', !!data?.recommendations);
        console.log('🔍 DEBUG - data.recommendations value:', data?.recommendations);
        console.log('🔍 DEBUG - Condition result:', res.ok && data && data.summary && data.recommendations);
        if (res.ok && data && data.summary && data.recommendations) {
          // Generar informe profesional con el nuevo formato
          try {
            const informe = `# Informe Profesional de Empleabilidad

## Resumen del Perfil
${data.summary}

## Nivel de Empleabilidad
**${data.level}** (Puntaje: ${data.employabilityScore}/100)

## Análisis Detallado

### Análisis del Perfil
${data.recommendations?.profile_analysis || 'Análisis del perfil basado en la evaluación completa.'}

### Análisis de Fortalezas
${data.recommendations?.strengths_analysis || 'Fortalezas identificadas en la evaluación.'}

### Áreas de Mejora
${data.recommendations?.improvement_areas || 'Áreas de mejora detectadas con recomendaciones.'}

### Análisis del CV
${data.recommendations?.cv_analysis || 'Análisis del CV realizado con herramientas especializadas.'}

## Sugerencias Laborales
${data.recommendations?.job_suggestions || 'Sugerencias laborales basadas en preferencias y habilidades.'}

## Próximos Pasos

### A Corto Plazo
${(safeGetRecommendations(data, 'recommendations.next_steps.short_term') || []).map((step: unknown) => `- ${String(step)}`).join('\n') || '- Actualizar CV\n- Crear perfil en LinkedIn'}

### A Medio Plazo
${(safeGetRecommendations(data, 'recommendations.next_steps.medium_term') || []).map((step: unknown) => `- ${String(step)}`).join('\n') || '- Completar formación específica\n- Ampliar red profesional'}

### A Largo Plazo
${(safeGetRecommendations(data, 'recommendations.next_steps.long_term') || []).map((step: unknown) => `- ${String(step)}`).join('\n') || '- Desarrollar especialización\n- Buscar oportunidades de liderazgo'}

## Recursos y Apoyo

${(safeGetRecommendations(data, 'recommendations.resources') || []).map((resource: unknown) => {
      const res = resource as { name?: string; description?: string; url?: string };
      return `### ${res.name || 'Recurso'}
${res.description || 'Descripción no disponible'}
[Acceder a ${res.name || 'Recurso'}](target="_blank" href="${res.url || '#'}")`;
    }).join('\n\n') || '### Recursos Generales\n- LinkedIn: Red profesional para networking\n- InfoJobs: Portal de empleo líder en España\n- Platzi: Plataforma de cursos online'}

## Habilidades Evaluadas
${filterValidSoftSkills(personal.softSkills || []).map((skill) => `- **${skill.skill}**: ${skill.score}% (${skill.level})`).join('\n') || 'No se evaluaron habilidades soft'}

### Preferencias Laborales
- **Áreas de interés**: ${(() => {
    const areas = data?.report?.jobPreferences?.areas;
    return (areas && Array.isArray(areas) && areas.length > 0) ? areas.join(', ') : 'No especificadas';
  })()}
- **Modalidad de trabajo**: ${data?.report?.jobPreferences?.workMode || 'No especificada'}
- **Disponibilidad**: ${data?.report?.jobPreferences?.availability || 'No especificada'}

---
*Informe profesional generado el ${data.createdAt ? new Date(data.createdAt).toLocaleDateString('es-ES') : new Date().toLocaleDateString('es-ES')}*
          `;
            console.log('✅ DEBUG - Informe generado exitosamente. Longitud:', informe.length);
            console.log('✅ DEBUG - Primeros 200 caracteres:', informe.substring(0, 200));
            setIaReport(informe);
            console.log('✅ DEBUG - Estado iaReport actualizado');
          } catch (error) {
            console.error('❌ Error generando informe:', error);
            setErrorIa('Error al generar el informe. Se generará un informe básico.');
          }
        } else {
          console.log('❌ DEBUG - Condición falló. Motivos:');
          console.log('  - res.ok:', res.ok);
          console.log('  - data:', !!data);
          console.log('  - data.summary:', !!data?.summary);
          console.log('  - data.recommendations:', !!data?.recommendations);
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
    // Solo llamar si hay datos suficientes
    // Verificar tanto personal.softSkills como report?.softSkills
    const hasPersonalSoftSkills = validateSoftSkills(personal.softSkills);
    const hasReportSoftSkills = validateSoftSkills(report?.softSkills || []);
    const hasSoftSkills = hasPersonalSoftSkills || hasReportSoftSkills;
    
    if (hasSoftSkills) {
      // Condición cumplida - Ejecutando fetchIaReport
      // console.log('✅ CONDICIÓN CUMPLIDA - Ejecutando fetchIaReport');
      fetchIaReport();
    } else {
      // Condición no cumplida - No se ejecuta fetchIaReport
      // console.log('❌ CONDICIÓN NO CUMPLIDA - No se ejecuta fetchIaReport');
      // console.log('  • hasPersonalSoftSkills:', hasPersonalSoftSkills);
      // console.log('  • hasReportSoftSkills:', hasReportSoftSkills);
    }
  }, [report?.jobPreferences, personal.softSkills, report?.softSkills, cvAnalysis, game?.completedGames, report?.firstName, report?.lastName, report?.userId]);

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

  // Estado para la descarga de PDF
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [pdfError, setPdfError] = useState('');

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

  // Función para descargar PDF
  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    setPdfError('');
    
    // Datos para PDF preparados
    
    try {
      const requestBody = {
        userId: report?.userId || 'user',
        fullName: `${report?.firstName || ''} ${report?.lastName || ''}`.trim() || 'Usuario',
        softSkills: filterValidSoftSkills(personal.softSkills || []).map((skill) => ({
          skill: skill.skill,
          score: skill.score,
          level: typeof skill.level === 'string' ? skill.level.charAt(0).toUpperCase() + skill.level.slice(1) : 'Bajo',
          confidence: skill.confidence,
        })),
        cvAnalysis: personal.cvAnalysis ? {
          strengths: personal.cvAnalysis.strengths ?? [],
          weaknesses: personal.cvAnalysis.weaknesses ?? [],
          feedback: personal.cvAnalysis.feedback ?? '',
          structure: personal.cvAnalysis.structure ?? 'regular',
          coherence: personal.cvAnalysis.coherence ?? 'regular',
          experience: personal.cvAnalysis.experience ?? 'regular',
          skills: personal.cvAnalysis.skills ?? [],
          education: personal.cvAnalysis.education ?? [],
          alerts: personal.cvAnalysis.alerts ?? [],
        } : null,
        jobPreferences: personal.jobPreferences || null,
        completedGames: game?.completedGames || [],
        logs: []
      };
      
              // Request body para PDF preparado

      const response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.PDF_DOWNLOAD), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      // Obtener el blob del PDF
      const blob = await response.blob();
      
      // Crear URL del blob
      const url = window.URL.createObjectURL(blob);
      
      // Crear enlace de descarga
      const link = document.createElement('a');
      link.href = url;
      link.download = `informe_empleabilidad_${requestBody.fullName.replace(/\s+/g, '_')}_${new Date().toISOString().slice(0, 10)}.pdf`;
      
      // Simular clic para descargar
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Limpiar URL
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
              // Error descargando PDF
      setPdfError('Error al descargar el PDF. Por favor, inténtalo de nuevo.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  // Función para imprimir
  const handlePrint = () => {
    window.print();
  };

  // 1. Portada
  const portada = (
    <div className="bg-white rounded-lg shadow-md p-8 flex flex-col items-center mb-8 print-report-section print-page-break-inside-avoid">
      <img src={logo} alt="Logo EvalúaTE" className="w-32 mb-4" />
      <h1 className="text-4xl font-bold mb-2">Informe de Empleabilidad</h1>
      <h2 className="text-2xl font-semibold mb-1">{report?.firstName} {report?.lastName}</h2>
      <p className="text-gray-600">{fecha}</p>
      
      {/* Botones de acción */}
      <div className="flex gap-4 mt-6 print-hidden">
        <button
          onClick={handleDownloadPdf}
          disabled={downloadingPdf || !iaReport}
          className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
            downloadingPdf || !iaReport
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {downloadingPdf ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Generando PDF...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Descargar PDF
            </span>
          )}
        </button>
        
        <button
          onClick={handlePrint}
          disabled={!iaReport}
          className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
            !iaReport
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-green-600 text-white hover:bg-green-700'
          }`}
        >
          <span className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            Imprimir
          </span>
        </button>
      </div>
      
      {/* Mensaje de error del PDF */}
      {pdfError && (
        <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg print-hidden">
          {pdfError}
        </div>
      )}
    </div>
  );

  // 2. Mapa de habilidades (Radar + resumen)
  // Usar useMemo para evitar recalcular en cada render
  const radarDataFromIa = useMemo(() => iaReport ? extractRadarData(iaReport) : [], [iaReport]);

  // Función para eliminar duplicados y asegurar claves únicas
  const processRadarData = (data: Array<{ skill?: string; softskill?: string; score: number }>) => {
    if (!Array.isArray(data)) {
      console.warn("processRadarData: data is not an array, returning empty array");
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

  const radarData = radarDataFromIa.length > 0
    ? processRadarData(radarDataFromIa)
    : processRadarData(filterValidSoftSkills(personal.softSkills || []));
  const radar = (
    <div className="bg-white rounded-lg shadow-md p-8 mb-8 print-report-section print-page-break-inside-avoid">
      <h2 className="text-2xl font-bold mb-4">Mapa de habilidades</h2>
      <div className="flex flex-col md:flex-row gap-8 items-center">
        <div className="w-full md:w-1/2 h-96">
          {radarData.length > 0 ? (
            <ResponsiveRadar
              data={radarData}
              keys={["score"]}
              indexBy="softskill"
              margin={{ top: 40, right: 80, bottom: 40, left: 80 }}
              borderColor={{ from: 'color' }}
              gridLabelOffset={20}
              dotSize={12}
              dotColor={{ theme: 'background' }}
              dotBorderWidth={2}
              dotBorderColor={{ from: 'color' }}
              colors={{ scheme: 'nivo' }}
              fillOpacity={0.25}
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
            {filterValidSoftSkills(personal.softSkills || []).map((skill, idx: number) => (
              <li key={idx}>
                <span className="font-medium">{skill.skill}:</span> {skill.score}%
              </li>
            ))}
          </ul>
          <p className="font-semibold mt-2">
            Puntaje global de empleabilidad: {report?.employabilityScore ?? '-'}
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
        <div className="bg-blue-100 rounded-lg shadow-md p-6 mb-8 text-center">
          <p className="text-lg font-semibold mb-4">Generando tu informe personalizado</p>
          <div className="w-full flex justify-center">
            <div className="w-2/3 bg-blue-200 rounded-full h-3 overflow-hidden">
              <div
                className="bg-blue-500 h-3 transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
          <p className="mt-4 text-xs text-gray-500">Esto puede tardar unos segundos. Por favor, ten paciencia.</p>
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
      {(() => { console.log('🔍 DEBUG - Estado actual iaReport:', !!iaReport, 'Longitud:', iaReport?.length || 0); return null; })()}
      {iaReport && (
        <>
          <div className="informe-empleabilidad report-container">
            <div className="report-content professional-report">
              <ReactMarkdown
                components={{
                  // Configuración mejorada para renderizado profesional
                  h1: ({ children, ...props }) => (
                    <h1 {...props} className="text-3xl font-bold text-gray-900 mb-6 mt-8 pb-2 border-b-2 border-gray-200">
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
                    <blockquote {...props} className="border-l-4 border-blue-500 pl-4 italic text-gray-600 bg-blue-50 py-2 rounded-r">
                      {children}
                    </blockquote>
                  ),
                  code: ({ children, ...props }) => (
                    <code {...props} className="bg-gray-100 px-2 py-1 rounded text-sm font-mono text-gray-800">
                      {children}
                    </code>
                  ),
                  pre: ({ children, ...props }) => (
                    <pre {...props} className="bg-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono text-gray-800 border">
                      {children}
                    </pre>
                  ),
                  table: ({ children, ...props }) => (
                    <div className="overflow-x-auto mb-4">
                      <table {...props} className="min-w-full border-collapse border border-gray-300">
                        {children}
                      </table>
                    </div>
                  ),
                  th: ({ children, ...props }) => (
                    <th {...props} className="border border-gray-300 px-4 py-2 bg-gray-50 font-semibold text-gray-900 text-left">
                      {children}
                    </th>
                  ),
                  td: ({ children, ...props }) => (
                    <td {...props} className="border border-gray-300 px-4 py-2 text-gray-700">
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
                    if (typeof children === 'string' && children.includes('★')) {
                      // Verificar si es una línea de indicadores de calidad
                      if (children.includes('Formato:') || children.includes('Claridad:') || children.includes('Información clave:') || children.includes('Ortografía:')) {
                        // Dividir el texto en partes para renderizar las estrellas con colores
                        const parts = children.split(/((?:★+)(?:☆*))/g);
                        
                                                 return (
                           <div {...props} className="quality-indicators">
                             <div className="text-gray-700 leading-relaxed">
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
                             </div>
                           </div>
                         );
                      } else {
                        // Para otras estrellas en el texto, usar el renderizado normal
                        const parts = children.split(/((?:★+)(?:☆*))/g);
                        
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

          {!feedbackSent && (
            <div className="bg-gray-50 rounded-lg shadow-md p-6 mb-8 print-hidden">
              <form onSubmit={handleFeedbackSubmit}>
                <label className="block mb-2 font-semibold">¿Te resultó útil este informe?</label>
                <div className="flex gap-4 mb-4">
                  <label className="flex items-center gap-1">
                    <input type="radio" name="rating" value="útil" required checked={feedback.rating === 'útil'} onChange={e => setFeedback(f => ({...f, rating: e.target.value}))} />
                    Útil
                  </label>
                  <label className="flex items-center gap-1">
                    <input type="radio" name="rating" value="no útil" required checked={feedback.rating === 'no útil'} onChange={e => setFeedback(f => ({...f, rating: e.target.value}))} />
                    No útil
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