// src/pages/ResultadosPage.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '../app/hooks';
import type { RootState } from '../app/store';
import { ResponsiveRadar } from '@nivo/radar';
import type { SoftSkillResult, UserDecision } from '../types/skills';

// Componentes visuales

const ResultadosPage: React.FC = () => {
  const navigate = useNavigate();
  const [toast, setToast] = useState<string | null>(null);

  // Accedemos al estado global tipado
  // Ajusta el selector según la estructura real de tu store
  const personal = useAppSelector((state: RootState) => state.personal);
  const cvAnalysis = personal?.cvAnalysis;

  // Verificamos que todo el progreso sea completo antes de mostrar resultados
  useEffect(() => {
    if ((personal?.report?.completedGames?.length ?? 0) < 10 || !cvAnalysis || (personal?.report?.softSkills?.length ?? 0) === 0) {
      navigate('/games');
    }
  }, [personal?.report?.completedGames, cvAnalysis, personal?.report?.softSkills, navigate]);

  // Datos para gráfico radar
  interface RadarData {
    skill: string;
    level: number;
    interactions: string[];
  }

  // Normaliza los datos de softSkills para asegurar que cumplen el tipo SoftSkillResult
  function normalizeSoftSkills(skills: unknown[]): SoftSkillResult[] {
    return (skills ?? []).map((skill: unknown) => ({
      skill: (skill as { skill: string }).skill,
      level: (skill as { level: string }).level as 'Bajo' | 'Medio' | 'Alto',
      confidence: (skill as { confidence?: number; score?: number }).confidence ?? (typeof (skill as { score?: number }).score === 'number' ? (skill as { score: number }).score / 100 : 0),
      feedback: (skill as { feedback?: string }).feedback ?? '',
      interactions: (skill as { interactions?: UserDecision[] }).interactions ?? [],
    }));
  }

  const normalizedSoftSkills: SoftSkillResult[] = normalizeSoftSkills(personal?.report?.softSkills ?? []);
  const data: RadarData[] = normalizedSoftSkills.map((skill) => ({
    skill: skill.skill,
    level: skill.confidence * 100,
    interactions: skill.interactions.map((i) => i.optionText ?? ''),
  }));

  // Áreas a mejorar (habilidades con menor puntuación)
  interface AreaMejorar {
    skill: string;
    level: string;
    confidence: number;
    feedback?: string;
    interactions: UserDecision[];
  }

  const areasToImprove: AreaMejorar[] = normalizedSoftSkills
    .filter((skill) => skill.confidence < 0.7)
    .map((skill) => ({
      skill: skill.skill,
      level: skill.level,
      confidence: skill.confidence,
      feedback: skill.feedback,
      interactions: skill.interactions
    }));

  // Manejador para descargar informe PDF
  const handleDownloadReport = async () => {
    try {
      // console.log('Descargando reporte...');
      const response = await fetch('/api/reports/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: personal.report?.userId,
          reportData: personal.report,
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reporte-empleabilidad-${personal.firstName}-${personal.lastName}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        setToast('Reporte descargado exitosamente');
      } else {
        setToast('Error al descargar el reporte');
      }
    } catch {
      // console.log('Error descargando reporte:', error);
      setToast('Error al descargar el reporte');
    }
  };

  // Autoocultar notificaciones tras 3s
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const strengths = (personal.cvAnalysis as { strengths?: string[] })?.strengths ?? [];
  const weaknesses = (personal.cvAnalysis as { weaknesses?: string[] })?.weaknesses ?? [];

  return (
    <section className="relative max-w-4xl mx-auto p-6 space-y-8">
      {/* Título */}
      <h1 className="text-3xl font-bold text-center">Tu Informe Final</h1>

      {/* Notificación tipo Toast */}
      {toast && (
        <div className="fixed bottom-6 right-6 bg-black bg-opacity-75 text-white px-4 py-2 rounded shadow-lg">
          {toast}
        </div>
      )}

      {/* Análisis del CV */}
      {personal.cvAnalysis && (
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h3 className="text-xl font-semibold mb-4">📄 Análisis de tu CV</h3>
          
          {/* Puntuación general */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">Puntuación general:</span>
              <span className="text-2xl font-bold text-blue-600">
                {typeof personal.cvAnalysis === 'object' && personal.cvAnalysis && 'score' in personal.cvAnalysis
                  ? (personal.cvAnalysis as { score?: number }).score ?? 'N/A'
                  : 'N/A'}
              </span>
            </div>
          </div>

          {/* Fortalezas */}
          {strengths.length > 0 && (
            <div className="mb-6">
              <h4 className="font-semibold mb-3 text-green-700">✅ Fortalezas identificadas:</h4>
              <ul className="space-y-2">
                {strengths.map((strength, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-green-500 mr-2">•</span>
                        <span className="text-gray-700">{strength}</span>
                      </li>
                    ))}
              </ul>
            </div>
          )}

          {/* Áreas de mejora */}
          {weaknesses.length > 0 && (
            <div>
              <h4 className="font-semibold mb-3 text-orange-700">🔧 Áreas de mejora:</h4>
              <ul className="space-y-2">
                {weaknesses.map((weakness, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-orange-500 mr-2">•</span>
                        <span className="text-gray-700">{weakness}</span>
                      </li>
                    ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* B. Habilidades blandas evaluadas */}
      {normalizedSoftSkills.length > 0 ? (
        <div className="bg-white p-6 rounded shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Habilidades Blandas Evaluadas</h2>
          <ul className="space-y-2">
            {normalizedSoftSkills.map((skill, index) => (
              <li key={index}>
                <span className="font-medium">{skill.skill}:</span> Nivel: {skill.level} ({Math.round(skill.confidence * 100)}% de confianza)
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="bg-yellow-50 p-4 border border-yellow-200 rounded">
          No se han evaluado habilidades blandas aún.
        </div>
      )}

      {/* C. Gráfico Radar */}
      <div className="w-full h-96">
        <ResponsiveRadar
          data={data as unknown as Record<string, unknown>[]}
          keys={['level']}
          indexBy="skill"
          margin={{ top: 70, right: 80, bottom: 70, left: 80 }}
          borderColor="#3182eb"
          dotSize={10}
          dotColor="#2563eb"
          dotBorderWidth={2}
          enableDots={true}
          animate={true}
        />
      </div>

      {/* D. Recomendaciones */}
      <div className="bg-blue-50 p-6 rounded shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Recomendaciones de mejora</h2>
        <ul className="space-y-2">
          {areasToImprove.length > 0 ? (
            areasToImprove.map((skill, index) => (
              <li key={index}>
                <strong>{skill.skill}:</strong> Tu nivel es <em>{skill.level}</em>. Recomendación: {skill.feedback}
              </li>
            ))
          ) : (
            <li>No hay recomendaciones disponibles aún.</li>
          )}
        </ul>
      </div>

      {/* E. Fortalezas más destacadas */}
      <div className="bg-green-50 p-6 rounded shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Fortalezas más destacadas</h2>
        <ul className="space-y-2">
          {normalizedSoftSkills.filter((skill) => skill.confidence >= 0.8).map((skill, index) => (
            <li key={index}>
              <strong>{skill.skill}:</strong> Nivel: <em>{skill.level}</em> ({Math.round(skill.confidence * 100)}% de confianza)
            </li>
          ))}
        </ul>
      </div>

      {/* F. Áreas a mejorar */}
      <div className="bg-red-50 p-6 rounded shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Áreas a mejorar</h2>
        <ul className="space-y-2">
          {areasToImprove.length > 0 ? (
            areasToImprove.map((skill, index) => (
              <li key={index}>
                <strong>{skill.skill}:</strong> Nivel: <em>{skill.level}</em> ({Math.round(skill.confidence * 100)}% de confianza). Recomendación: {skill.feedback}
              </li>
            ))
          ) : (
            <li>No hay áreas a mejorar según el análisis.</li>
          )}
        </ul>
      </div>

      {/* G. Resumen de habilidades */}
      <div className="bg-white p-6 rounded shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Resumen de habilidades</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="font-medium">Puntaje global de empleabilidad:</h3>
            <p className="text-xl font-bold">{personal?.report?.employabilityScore ?? 0}</p>
          </div>
          <div>
            <h3 className="font-medium">Nivel de empleabilidad:</h3>
            <p className="text-xl font-bold">{personal?.report?.level ?? ''}</p>
          </div>
          <div>
            <h3 className="font-medium">Puntaje ajustado:</h3>
            <p className="text-xl font-bold">{personal?.report?.adjustedScore ?? 0}</p>
          </div>
        </div>
      </div>

      {/* H. Botón de descarga */}
      <div className="flex justify-center mt-6">
        <button
          onClick={handleDownloadReport}
          className={`py-3 px-6 bg-green-600 text-white rounded hover:bg-green-700 transition-colors`}
        >
          Descargar Informe PDF
        </button>
      </div>
    </section>
  );
};

export default ResultadosPage;