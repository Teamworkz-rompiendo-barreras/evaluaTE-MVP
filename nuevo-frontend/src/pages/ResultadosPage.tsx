// src/pages/ResultadosPage.tsx
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppSelector } from '../app/hooks'

// Tipos desde personalSlice
import {
  SoftSkillResult,
  CvAnalysis,
} from '../features/personal/personalSlice'

// Componente de Nivo
import { ResponsiveRadar } from '@nivo/radar'

export default function ResultadosPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  // Accedemos al estado global tipado
  const personal = useAppSelector((state) => state.personal)
  const cvAnalysis = personal.cvAnalysis as CvAnalysis | undefined
  const softSkills = personal.softSkills || []

  // Obtenemos juegos completados
  const completedGames = useAppSelector(
    (state) => state.progress.completedGames || []
  )

  // Verificamos que todo el progreso sea completo antes de mostrar resultados
  useEffect(() => {
    if (completedGames.length < 10 || !cvAnalysis) {
      navigate('/games')
    }
  }, [completedGames, cvAnalysis, navigate])

  // Datos para el gráfico radar
  const data = [
    {
      skill: 'Toma de decisiones',
      level:
        softSkills.find((s) => s.skill === 'Toma de decisiones')?.confidence *
          100 || 0,
    },
    {
      skill: 'Resolución de problemas',
      level:
        softSkills.find((s) => s.skill === 'Resolución de problemas')
          ?.confidence * 100 || 0,
    },
    {
      skill: 'Trabajo en equipo',
      level:
        softSkills.find((s) => s.skill === 'Trabajo en equipo')?.confidence *
          100 || 0,
    },
    {
      skill: 'Gestión emocional',
      level:
        softSkills.find((s) => s.skill === 'Gestión emocional')?.confidence *
          100 || 0,
    },
    {
      skill: 'Comunicación',
      level:
        softSkills.find((s) => s.skill === 'Comunicación')?.confidence * 100 ||
        0,
    },
    {
      skill: 'Curiosidad y aprendizaje continuo',
      level:
        softSkills.find(
          (s) => s.skill === 'Curiosidad y aprendizaje continuo'
        )?.confidence * 100 || 0,
    },
    {
      skill: 'Creatividad',
      level:
        softSkills.find((s) => s.skill === 'Creatividad')?.confidence * 100 || 0,
    },
    {
      skill: 'Flexibilidad',
      level:
        softSkills.find((s) => s.skill === 'Flexibilidad')?.confidence * 100 ||
        0,
    },
    {
      skill: 'Pensamiento crítico',
      level:
        softSkills.find((s) => s.skill === 'Pensamiento crítico')?.confidence *
          100 || 0,
    },
    {
      skill: 'Autonomía',
      level:
        softSkills.find((s) => s.skill === 'Autonomía')?.confidence * 100 || 0,
    },
  ]

  // Creamos listas de fortalezas y áreas a mejorar
  const fortalezas = softSkills.filter((skill) => skill.level === 'Alto')
  const areasMejorar = softSkills.filter((skill) => skill.level !== 'Alto')

  // Manejador para descargar informe
  const handleDownloadReport = async () => {
    setLoading(true)
    try {
      const payload = { softSkills, cvAnalysis }
      const resp = await fetch('/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

      const blob = await resp.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'informe-resultados.pdf'
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      setToast('Informe descargado correctamente')
    } catch (err) {
      console.error(err)
      setToast('Error al generar el informe. Intenta más tarde.')
    } finally {
      setLoading(false)
    }
  }

  // Autoocultar toast tras 3s
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

      {/* Toast Notification */}
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

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium mb-2">Fortalezas</h3>
              <ul className="list-disc ml-6">
                {cvAnalysis.strengths.length > 0 ? (
                  cvAnalysis.strengths.map((str, i) => (
                    <li key={i}>{str}</li>
                  ))
                ) : (
                  <p className="text-gray-500">No se encontraron fortalezas.</p>
                )}
              </ul>
            </div>
            <div>
              <h3 className="font-medium mb-2">Áreas a mejorar</h3>
              <ul className="list-disc ml-6">
                {cvAnalysis.weaknesses.length > 0 ? (
                  cvAnalysis.weaknesses.map((w, i) => <li key={i}>{w}</li>)
                ) : (
                  <p className="text-gray-500">
                    Tu CV está bien estructurado.
                  </p>
                )}
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <p className="text-center text-gray-500">
          No hay análisis de CV disponible aún.
        </p>
      )}

      {/* B. Evaluación de habilidades blandas */}
      <div className="bg-white p-6 rounded shadow-md">
        <h2 className="text-2xl font-semibold mb-4">
          Minijuegos Completados
        </h2>

        {/* Gráfico radar */}
        <div style={{ height: '400px', width: '100%' }}>
          <ResponsiveRadar
            data={data}
            keys={['level']}
            indexBy="skill"
            maxValue="auto"
            margin={{ top: 40, right: 120, bottom: 70, left: 120 }}
            borderColor="#3182ce"
            gridShape="linear"
            dotSize={10}
            dotColor="#2563eb"
            dotBorderWidth={2}
            enableDots={true}
            animate={true}
          />
        </div>

        {/* Listado de habilidades */}
        <div className="mt-8">
          <h3 className="font-medium mb-2">Puntos fuertes:</h3>
          <ul className="list-disc ml-6 mb-4">
            {fortalezas.length > 0 ? (
              fortalezas.map((d, idx) => (
                <li key={idx}>
                  {d.skill}: {d.level} ({Math.round(d.confidence * 100)}%{' '}
                  confianza)
                </li>
              ))
            ) : (
              <p className="text-gray-500">
                Todavía no tienes puntos fuertes identificados.
              </p>
            )}
          </ul>

          <h3 className="font-medium mb-2">Áreas a mejorar:</h3>
          <ul className="list-disc ml-6">
            {areasMejorar.length > 0 ? (
              areasMejorar.map((d, idx) => (
                <li key={idx}>
                  {d.skill}: {d.level} ({Math.round(d.confidence * 100)}%{' '}
                  confianza)
                </li>
              ))
            ) : (
              <p className="text-gray-500">
                ¡Felicidades! Has desarrollado todas tus áreas clave.
              </p>
            )}
          </ul>
        </div>
      </div>

      {/* C. Recomendaciones laborales */}
      <div className="bg-blue-50 p-6 rounded shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Recomendaciones Laborales</h2>

        <div className="space-y-2">
          <p>
            <span className="font-medium">Tipo de trabajo recomendado:</span>{' '}
            {personal.jobPreferences || 'No especificado'}
          </p>
          <p>
            <span className="font-medium">Modalidad ideal:</span>{' '}
            {personal.workMode || 'No especificado'}
          </p>
          <p>
            <span className="font-medium">Disponibilidad horaria:</span>{' '}
            {personal.availability || 'No especificado'}
          </p>
          <p>
            <span className="font-medium">Incorporación:</span>{' '}
            {personal.startDate || 'No especificado'}
          </p>
          <p>
            <span className="font-medium">Certificado de discapacidad:</span>{' '}
            {personal.hasDisabilityCert ? 'Sí' : 'No'}
          </p>
        </div>

        <div className="mt-6">
          <h3 className="font-medium mb-2">Próximos pasos sugeridos</h3>
          <ul className="list-disc ml-6">
            <li>Enviar tu informe a un acompañante</li>
            <li>Explorar formaciones recomendadas</li>
            <li>Buscar empleo según tus puntos fuertes</li>
          </ul>
        </div>
      </div>

      {/* D. Botones de acción */}
      <div className="flex flex-col md:flex-row justify-center gap-4 mt-6">
        <button
          onClick={() => navigate('/games')}
          disabled={completedGames.length < 10}
          className={`px-6 py-2 rounded transition ${
            completedGames.length < 10
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          Volver al Dashboard
        </button>
        <button
          onClick={handleDownloadReport}
          disabled={loading}
          className="flex items-center justify-center px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition disabled:opacity-50"
        >
          {loading && (
            <svg
              className="animate-spin h-5 w-5 mr-2 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
              />
            </svg>
          )}
          {loading ? 'Generando informe...' : 'Descargar Informe'}
        </button>
      </div>
    </section>
  )
}