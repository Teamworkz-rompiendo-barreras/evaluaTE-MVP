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

  // 6. Análisis del CV (breve y amable)
  const cvSection = (
    <div className="bg-white rounded-lg shadow-md p-8 mb-8">
      <h2 className="text-2xl font-bold mb-4">Análisis de tu CV</h2>
      {cvAnalysis ? (
        <div>
          <p className="mb-2">¡Gracias por compartir tu CV! Hemos detectado los siguientes puntos:</p>
          <ul className="list-disc ml-6 mb-2">
            <li><strong>Estructura:</strong> {cvAnalysis.structure}</li>
            <li><strong>Coherencia:</strong> {cvAnalysis.coherence}</li>
            <li><strong>Experiencia:</strong> {cvAnalysis.experience}</li>
            <li><strong>Habilidades técnicas:</strong> {(cvAnalysis.skills ?? []).join(', ')}</li>
            {cvAnalysis.education && <li><strong>Formación:</strong> {cvAnalysis.education.join(', ')}</li>}
            {cvAnalysis.alerts && <li><strong>Áreas de mejora:</strong> {cvAnalysis.alerts.join(', ')}</li>}
          </ul>
          <p className="text-green-700">Recuerda que tu CV es una herramienta viva: actualízalo con tus logros y aprendizajes.</p>
        </div>
      ) : (
        <p>No se ha podido analizar el CV en este momento.</p>
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
      {/* Informe IA generado */}
      <div className="bg-blue-100 rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-2xl font-bold mb-4">Informe personalizado generado por IA</h2>
        {loadingIa && <p>Generando informe con IA...</p>}
        {errorIa && <p className="text-red-600">{errorIa}</p>}
        {iaReport && <div className="prose max-w-none"><ReactMarkdown>{iaReport}</ReactMarkdown></div>}
        {/* Formulario de feedback */}
        {iaReport && !feedbackSent && (
          <form className="mt-6" onSubmit={handleFeedbackSubmit}>
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
        )}
        {feedbackSent && <p className="text-green-700 mt-4">¡Gracias por tu feedback!</p>}
      </div>
      {portada}
      {radar}
      {fortalezasSection}
      {areasMejoraSection}
      {recomendacionesSection}
      {cvSection}
      {pasosSection}
    </section>
  );
};

export default ResultadosPage;