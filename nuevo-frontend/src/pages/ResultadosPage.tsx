// src/pages/ResultadosPage.tsx
import React, { useEffect, useState } from 'react';
import { useAppSelector } from '../app/hooks';
import type { RootState } from '../app/store';
import { ResponsiveRadar } from '@nivo/radar';
import logo from '../assets/Logo_teamworkz.png';
import { buildApiUrl, API_CONFIG } from '../config/api';
import { games } from '../data/games'; // Importar el array global de juegos
import ReactMarkdown from 'react-markdown';
import { useMemo } from 'react';

// Función para extraer el bloque JSON radarData del Markdown
function extractRadarData(markdown: string): any[] {
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
  const game = useAppSelector((state: RootState) => state.game); // <-- Añadir esta línea

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
        const res = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.IA_REPORT), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            userId: report?.userId || 'user-unknown',
            fullName: `${report?.firstName || ''} ${report?.lastName || ''}`.trim(),
            softSkills: (report?.softSkills ?? []).map(skill => ({
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
            } : undefined,
            jobPreferences: report?.jobPreferences || {},
            completedGames: Array.isArray(game?.completedGames)
              ? game.completedGames.map(id => {
                  const idx = games.findIndex(g => g.id === id);
                  return idx >= 0 ? idx + 1 : null;
                }).filter(n => typeof n === 'number' && !isNaN(n))
              : [],
            logs: []
          }),
        });
        const data = await res.json();
        if (res.ok && data.informe) {
          setIaReport(data.informe);
        } else {
          setErrorIa('No se pudo generar el informe IA.');
        }
      } catch (err) {
        setErrorIa('Error de conexión con el servicio de IA.');
      } finally {
        setLoadingIa(false);
      }
    };
    // Solo llamar si hay datos suficientes
    if (report?.jobPreferences && report?.softSkills && cvAnalysis) {
      fetchIaReport();
    }
  }, [report?.jobPreferences, report?.softSkills, cvAnalysis, game?.completedGames, report?.firstName, report?.lastName]);

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

  const radarData = radarDataFromIa.length > 0
    ? radarDataFromIa.map(item => ({
        softskill: item.skill,
        score: item.score,
      }))
    : (report?.softSkills ?? []).map(skill => ({
        softskill: skill.skill,
        score: skill.score,
      }));
  const radar = (
    <div className="bg-white rounded-lg shadow-md p-8 mb-8">
      <h2 className="text-2xl font-bold mb-4">Mapa de habilidades</h2>
      <div className="flex flex-col md:flex-row gap-8 items-center">
        <div className="w-full md:w-1/2 h-96">
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

  // 3. Fortalezas más destacadas
  const fortalezas = (report?.softSkills ?? []).filter(s => s.score >= 80);
  const fortalezasSection = (
    <div className="bg-green-50 rounded-lg shadow-md p-8 mb-8">
      <h2 className="text-2xl font-bold mb-4">Fortalezas más destacadas</h2>
      {fortalezas.length > 0 ? (
        <ul className="space-y-2">
          {fortalezas.map((skill, idx) => (
            <li key={idx}>
              <strong>{skill.skill}:</strong> {skill.level} ({skill.score}% confianza)
            </li>
          ))}
        </ul>
      ) : (
        <p>No se han identificado fortalezas destacadas aún.</p>
      )}
    </div>
  );

  // 4. Áreas de mejora + sugerencias prácticas
  const areasMejora = (report?.softSkills ?? []).filter(s => s.score < 70);
  const areasMejoraSection = (
    <div className="bg-red-50 rounded-lg shadow-md p-8 mb-8">
      <h2 className="text-2xl font-bold mb-4">Áreas de mejora y sugerencias</h2>
      {areasMejora.length > 0 ? (
        <ul className="space-y-2">
          {areasMejora.map((skill, idx) => (
            <li key={idx}>
              <strong>{skill.skill}:</strong> {skill.level} ({skill.score}% confianza). <br />
              <span className="text-sm">Sugerencia: Practica situaciones reales y pide feedback para mejorar esta habilidad.</span>
            </li>
          ))}
        </ul>
      ) : (
        <p>No hay áreas de mejora destacadas según el análisis actual.</p>
      )}
    </div>
  );

  // 5. Recomendaciones laborales (puestos, sectores, entorno)
  const recomendaciones = report?.recommendations ?? [];
  const recomendacionesSection = (
    <div className="bg-blue-50 rounded-lg shadow-md p-8 mb-8">
      <h2 className="text-2xl font-bold mb-4">Recomendaciones laborales</h2>
      {recomendaciones.length > 0 ? (
        <ul className="space-y-2">
          {recomendaciones.map((rec, idx) => (
            <li key={idx}>{rec}</li>
          ))}
        </ul>
      ) : (
        <p>No hay recomendaciones laborales específicas aún.</p>
      )}
    </div>
  );

  // 6. Análisis del CV
  const cvSection = (
    <div className="bg-white rounded-lg shadow-md p-8 mb-8">
      <h2 className="text-2xl font-bold mb-6 text-gray-800 text-center">Análisis de tu CV</h2>
      {cvAnalysis ? (
        <div className="space-y-6">
          {/* Feedback General */}
          {cvAnalysis.feedback && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Feedback General</h3>
              <p className="text-gray-600">{cvAnalysis.feedback}</p>
            </div>
          )}

          {/* Fortalezas y Debilidades */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Fortalezas */}
            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-green-800 mb-2">✓ Fortalezas</h3>
              {cvAnalysis.strengths && cvAnalysis.strengths.length > 0 ? (
                <ul className="list-disc list-inside space-y-1 text-green-700">
                  {cvAnalysis.strengths.map((item, i) => <li key={i}>{item}</li>)}
                </ul>
              ) : (
                <p className="text-gray-500">No se detectaron fortalezas específicas.</p>
              )}
            </div>

            {/* Debilidades */}
            <div className="bg-red-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-red-800 mb-2">→ Áreas de Mejora</h3>
              {cvAnalysis.weaknesses && cvAnalysis.weaknesses.length > 0 ? (
                <ul className="list-disc list-inside space-y-1 text-red-700">
                  {cvAnalysis.weaknesses.map((item, i) => <li key={i}>{item}</li>)}
                </ul>
              ) : (
                <p className="text-gray-500">No se detectaron áreas de mejora específicas.</p>
              )}
            </div>
          </div>

          {/* Otros detalles */}
          <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-800">
            <h3 className="font-semibold mb-2">Otros Detalles</h3>
            <p><strong>Estructura:</strong> {cvAnalysis.structure || 'No analizada'}</p>
            <p><strong>Coherencia:</strong> {cvAnalysis.coherence || 'No analizada'}</p>
            <p><strong>Habilidades Detectadas:</strong> {(cvAnalysis.skills && cvAnalysis.skills.length > 0) ? cvAnalysis.skills.join(', ') : 'Ninguna'}</p>
          </div>

        </div>
      ) : (
        <p className="text-center text-gray-500">No se ha podido analizar el CV en este momento.</p>
      )}
    </div>
  );

  // 7. Próximos pasos sugeridos
  const pasos = [
    'Completa todos los minijuegos para mejorar tu perfil.',
    'Actualiza tu CV con los nuevos logros y habilidades.',
    'Solicita feedback a personas de confianza.',
    'Explora formaciones y recursos recomendados.',
    'Revisa tus preferencias laborales y adáptalas a tus intereses.'
  ];
  const pasosSection = (
    <div className="bg-yellow-50 rounded-lg shadow-md p-8 mb-8">
      <h2 className="text-2xl font-bold mb-4">Próximos pasos sugeridos</h2>
      <ul className="list-disc ml-6">
        {pasos.map((p, idx) => (
          <li key={idx}>{p}</li>
        ))}
      </ul>
    </div>
  );

  // Renderizado final
  return (
    <section className="max-w-4xl mx-auto p-4">
      {/* Mensaje de carga */}
      {loadingIa && (
        <div className="bg-blue-100 rounded-lg shadow-md p-6 mb-8 text-center">
          <p className="text-lg font-semibold">Generando tu informe personalizado con IA...</p>
          <p>Esto puede tardar unos segundos.</p>
        </div>
      )}

      {/* Mensaje de error */}
      {errorIa && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-md p-6 mb-8" role="alert">
          <strong className="font-bold">Error de conexión.</strong>
          <span className="block sm:inline"> No se pudo generar el informe en este momento. Por favor, inténtalo de nuevo más tarde.</span>
        </div>
      )}

      {/* Informe de la IA y formulario de feedback */}
      {iaReport && (
        <>
          <div className="bg-white rounded-lg shadow-md p-8 mb-8 prose max-w-none">
            <ReactMarkdown>{iaReport}</ReactMarkdown>
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

      {/* Contenido del informe que no depende de la IA */}
      {portada}
      {radar}
    </section>
  );
};

export default ResultadosPage;