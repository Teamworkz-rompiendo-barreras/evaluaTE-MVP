// src/pages/ResultadosPage.tsx
import React, { useEffect, useState } from 'react';
import { useAppSelector } from '../app/hooks';
import type { RootState } from '../app/store';
import { ResponsiveRadar } from '@nivo/radar';
import logo from '../assets/Logo_teamworkz.png';
import { buildApiUrl, API_CONFIG } from '../config/api';
import ReactMarkdown from 'react-markdown';
import { useMemo } from 'react';

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

const ResultadosPage: React.FC = () => {
  const personal = useAppSelector((state: RootState) => state.personal);
  const cvAnalysis = personal?.cvAnalysis;
  const report = personal?.report;
  const fecha = new Date().toLocaleDateString();
  const game = useAppSelector((state: RootState) => state.game);

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
          preferences: report?.jobPreferences || {},
          minigames: (report?.softSkills ?? []).map(skill => ({
            skill: skill.skill,
            level: typeof skill.level === 'string' ? skill.level.charAt(0).toUpperCase() + skill.level.slice(1) : 'Bajo',
            score: skill.score ?? 0,
            confidence: skill.confidence ?? skill.score ?? 0,
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
          } : {
            strengths: [],
            weaknesses: [],
            feedback: 'No se pudo analizar el CV',
            structure: 'regular',
            coherence: 'regular',
            experience: 'regular',
            skills: [],
            education: [],
            alerts: ['Análisis limitado del CV']
          }
        };

        const res = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.IA_REPORT), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody),
          signal: AbortSignal.timeout(45000), // Timeout de 45 segundos
        });
        const data = await res.json();
        if (res.ok && data.informe) {
          setIaReport(data.informe);
        } else {
          setErrorIa('No se pudo generar el informe IA.');
        }
      } catch (err) {
        console.error('Error en fetchIaReport:', err);
        if (err instanceof Error && err.name === 'TimeoutError') {
          setErrorIa('El informe está tardando más de lo esperado. Se generará un informe básico automáticamente.');
        } else if (err instanceof Error && err.message?.includes('Failed to fetch')) {
          setErrorIa('No se pudo conectar con el servidor. Verifica tu conexión a internet.');
        } else {
          setErrorIa('Error de conexión con el servicio de IA. Se generará un informe básico.');
        }
      } finally {
        setLoadingIa(false);
      }
    };
    // Solo llamar si hay datos suficientes
    if (report?.jobPreferences && report?.softSkills) {
      fetchIaReport();
    }
  }, [report?.jobPreferences, report?.softSkills, cvAnalysis, game?.completedGames, report?.firstName, report?.lastName, report?.userId]);

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
          userData: { preferences: report?.jobPreferences, minigames: report?.softSkills, cvAnalysis },
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

  // Efecto para animar la barra de progreso
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
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

  // 1. Portada
  const portada = (
    <div className="bg-white rounded-lg shadow-md p-8 flex flex-col items-center mb-8">
      <img src={logo} alt="Logo EvalúaTE" className="w-32 mb-4" />
      <h1 className="text-4xl font-bold mb-2">Informe de Empleabilidad</h1>
      <h2 className="text-2xl font-semibold mb-1">{report?.firstName} {report?.lastName}</h2>
      <p className="text-gray-600">{fecha}</p>
    </div>
  );

  // 2. Mapa de habilidades (Radar + resumen)
  // Usar useMemo para evitar recalcular en cada render
  const radarDataFromIa = useMemo(() => iaReport ? extractRadarData(iaReport) : [], [iaReport]);

  // Función para eliminar duplicados y asegurar claves únicas
  const processRadarData = (data: any[]) => {
    const seen = new Set();
    return data
      .map(item => ({
        softskill: item.skill || item.softskill,
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
    : processRadarData(report?.softSkills ?? []);
  const radar = (
    <div className="bg-white rounded-lg shadow-md p-8 mb-8">
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
            {(report?.softSkills ?? []).map((skill, idx) => (
              <li key={idx}>
                <span className="font-medium">{skill.skill}:</span> {skill.level} ({skill.score}% confianza)
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
    <section className="max-w-4xl mx-auto p-4">
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
      {iaReport && (
        <>
          <div className="bg-white rounded-lg shadow-md p-8 mb-8 prose max-w-none overflow-visible">
            <ReactMarkdown
              components={{
                a: (props) => (
                  <a {...props} target="_blank" rel="noopener noreferrer">
                    {props.children}
                  </a>
                ),
                p: (props) => (
                  <p {...props} className="mb-4" />
                ),
                h1: (props) => (
                  <h1 {...props} className="mb-6 mt-8" />
                ),
                h2: (props) => (
                  <h2 {...props} className="mb-4 mt-6" />
                ),
                h3: (props) => (
                  <h3 {...props} className="mb-3 mt-5" />
                ),
                ul: (props) => (
                  <ul {...props} className="mb-4 space-y-2" />
                ),
                ol: (props) => (
                  <ol {...props} className="mb-4 space-y-2" />
                ),
                li: (props) => (
                  <li {...props} className="mb-2" />
                ),
              }}
            >{iaReport}</ReactMarkdown>
          </div>

          {!feedbackSent && (
            <div className="bg-gray-50 rounded-lg shadow-md p-6 mb-8">
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
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg shadow-md p-6 mb-8" role="alert">
              <p className="font-semibold">¡Gracias por tu feedback!</p>
            </div>
          )}
        </>
      )}
    </section>
  );
};

export default ResultadosPage;