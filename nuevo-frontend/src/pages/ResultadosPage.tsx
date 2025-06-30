// src/pages/ResultadosPage.tsx
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppSelector } from '../app/hooks'

// Tipos desde Redux
import {
  CvAnalysis,
  SoftSkillResult,
  JobPreference,
} from '@/types/skills'

// Componentes visuales
import { ResponsiveRadar } from '@nivo/radar'
import ProgressBar from '../components/ProgressBar'

export default function ResultadosPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  // Accedemos al estado global tipado
  const personal = useAppSelector((state) => state.personal)
  const cvAnalysis = personal.cvAnalysis as CvAnalysis | undefined
  const softSkills = personal.softSkills || []
  const completedGames = useAppSelector((state) => state.progress.completedGames || [])

  // Verificamos que todo el progreso sea completo antes de mostrar resultados
  useEffect(() => {
    if (completedGames.length < 10 || !cvAnalysis || softSkills.length === 0) {
      navigate('/games')
    }
  }, [completedGames, cvAnalysis, softSkills])

  // Datos para gráfico radar
  const data = softSkills.map(skill => ({
    skill: skill.skill,
    level: skill.confidence * 100
  }))

  // Áreas a mejorar (confianza menor a 0.6)
  const areasMejorar = softSkills.filter(skill => skill.confidence < 0.6)

  // Manejador para descargar informe PDF
  const handleDownloadReport = async () => {
    setLoading(true)
    try {
      const payload = {
        softSkills,
        cvAnalysis
      }

      const resp = await fetch('/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

      const blob = await resp.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'informe-resultados.pdf'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      setToast('Informe descargado correctamente')
    } catch (err) {
      console.error(err)
      setToast('Error al generar el informe. Intenta más tarde.')
    } finally {
      setLoading(false)
    }
  }

  // Autoocultar notificaciones tras 3s
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000)
      return () => clearTimeout(timer)
    }
  }, [toast])

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

      {/* A. Análisis del CV */}
      {cvAnalysis ? (
        <div className="bg-gray-50 p-6 rounded shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Análisis de tu CV</h2>
          <p className="mb-4">
            Puntuación global: <strong>{cvAnalysis.score}%</strong>
          </p>

          <div className="space-y-2 mb-6">
            <h3 className="font-medium">Puntos fuertes:</h3>
            <ul className="list-disc pl-5">
              {cvAnalysis.strengths?.length > 0 ? (
                cvAnalysis.strengths.map((strength, index) => (
                  <li key={index}>{strength}</li>
                ))
              ) : (
                <li>No se encontraron puntos fuertes.</li>
              )}
            </ul>
          </div>

          <div className="space-y-2">
            <h3 className="font-medium">Áreas a mejorar:</h3>
            <ul className="list-disc pl-5">
              {cvAnalysis.weaknesses?.length > 0 ? (
                cvAnalysis.weaknesses.map((weakness, index) => (
                  <li key={index}>{weakness}</li>
                ))
              ) : (
                <li>No se encontraron áreas a mejorar.</li>
              )}
            </ul>
          </div>
        </div>
      ) : (
        <div className="bg-yellow-50 p-4 border border-yellow-200 rounded">
          No se ha cargado el análisis del CV.
        </div>
      )}

      {/* B. Habilidades blandas evaluadas */}
      {softSkills.length > 0 ? (
        <div className="bg-white p-6 rounded shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Habilidades Blandas Evaluadas</h2>
          <ul className="space-y-2">
            {softSkills.map((skill, index) => (
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
          data={data}
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
          {areasMejorar.length > 0 ? (
            areasMejorar.map((skill, index) => (
              <li key={index}>
                <strong>{skill.skill}:</strong> Tu nivel es <em>{skill.level}</em>. Recomendación: {skill.feedback}
              </li>
            ))
          ) : (
            <li>No hay recomendaciones disponibles aún.</li>
          )}
        </ul>
      </div>

      {/* E. Botón de descarga */}
      <div className="flex justify-center mt-6">
        <button
          onClick={handleDownloadReport}
          disabled={loading}
          className={`py-3 px-6 bg-green-600 text-white rounded hover:bg-green-700 transition-colors ${
            loading ? 'opacity-70 cursor-not-allowed' : ''
          }`}
        >
          {loading ? 'Generando informe...' : 'Descargar Informe PDF'}
        </button>
      </div>
    </section>
  )
}