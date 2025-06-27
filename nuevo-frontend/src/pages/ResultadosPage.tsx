// src/pages/ResultadosPage.tsx
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppSelector } from '../app/hooks'

// Importamos los tipos desde personalSlice donde sí están definidos correctamente
import { PersonalState as PersonalStateFromSlice } from '../features/personal/personalSlice'

// Interfaz del análisis de CV
interface CvAnalysis {
  score: number
  strengths: string[]
  weaknesses: string[]
}

// Interfaz para habilidades blandas
interface SoftSkillResult {
  skill: string
  level: 'Bajo' | 'Medio' | 'Alto'
  confidence: number
}

export default function ResultadosPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  // Usamos el tipo correcto desde personalSlice
  const personal = useAppSelector(state => state.personal) as PersonalStateFromSlice
  const cvAnalysis = personal.cvAnalysis as CvAnalysis | undefined

  // Obtenemos los minijuegos completados
  const completedGames = useAppSelector(state => state.progress.completedGames)

  // Definimos las habilidades (deberían venir del backend o ser dinámicas)
  const skills = [
    "Comunicación",
    "Trabajo en equipo",
    "Autonomía",
    "Gestión del tiempo",
    "Flexibilidad",
    "Pensamiento crítico",
    "Resolución de problemas",
    "Creatividad",
    "Empatía",
    "Liderazgo"
  ]

  // Creamos datos ficticios basados en si el juego fue completado
  const gameData = skills.map((skill, index) => ({
    subject: skill,
    level: completedGames.includes(String(index + 1)) ? 'Alto' : 'Bajo'
  }))

  const fortalezas = gameData.filter(d => d.level === 'Alto')
  const areasMejorar = gameData.filter(d => d.level !== 'Alto')

  // Handler para descargar informe PDF
  const handleDownloadReport = async () => {
    setLoading(true)
    try {
      const payload = { gameData, cvAnalysis }
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
    <section className="relative max-w-3xl mx-auto p-6 space-y-8">
      <h1 className="text-3xl font-bold text-center">Tu Informe de Resultados</h1>

      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-6 right-6 bg-black bg-opacity-75 text-white px-4 py-2 rounded shadow-lg">
          {toast}
        </div>
      )}

      {/* Análisis de CV */}
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
                  cvAnalysis.strengths.map((str, i) => <li key={i}>{str}</li>)
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
                  <p className="text-gray-500">Tu CV está bien estructurado.</p>
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

      {/* Evaluación de habilidades blandas */}
      <div className="bg-white p-6 rounded shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Minijuegos Completados</h2>

        {/* Simulación de gráfico radar */}
        <div className="mb-6 p-4 bg-gray-100 rounded text-sm text-gray-700 text-center">
          📊 Aquí iría un gráfico tipo radar mostrando tus niveles por habilidad blanda.
        </div>

        {/* Listado de habilidades */}
        <div className="space-y-4">
          <h3 className="font-medium">Puntos fuertes</h3>
          {fortalezas.length > 0 ? (
            <ul className="list-disc ml-6 mb-4">
              {fortalezas.map(d => (
                <li key={d.subject}>
                  {d.subject} – <span className="font-semibold">{d.level}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 mb-4">Todavía no tienes puntos fuertes identificados.</p>
          )}

          <h3 className="font-medium">Áreas a mejorar</h3>
          {areasMejorar.length > 0 ? (
            <ul className="list-disc ml-6">
              {areasMejorar.map(d => (
                <li key={d.subject}>
                  {d.subject} – <span className="font-semibold">{d.level}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">¡Felicidades! Has desarrollado todas tus áreas clave.</p>
          )}
        </div>
      </div>

      {/* Botones de acción */}
      <div className="flex flex-col md:flex-row justify-center gap-4">
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