// src/pages/ResultadosPage.tsx
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppSelector } from '../app/hooks'
import type { CvAnalysis } from '../features/personal/personalSlice'

// Para renderizar los resultados de los minijuegos
interface GameResult {
  subject: string
  dA: number
}

export default function ResultadosPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  // 1️⃣ Leemos el análisis del CV (puede ser undefined)
  const cvAnalysis = useAppSelector(
    state => state.personal.cvAnalysis as CvAnalysis | undefined
  )

  // 2️⃣ Leemos el progreso de los minijuegos
  const completed = useAppSelector(state => state.progress.completed)

  // 3️⃣ Construimos un array para los minijuegos
  const gameData: GameResult[] = Object.keys(completed).map(key => ({
    subject: `Minijuego ${key}`,
    dA: completed[Number(key)] ? 100 : 0,
  }))

  const fortalezas = gameData.filter(d => d.dA >= 75)
  const areasMejorar = gameData.filter(d => d.dA < 75)

  // 7️⃣ Handler para descargar informe PDF
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
    <section className="relative max-w-2xl mx-auto p-6 space-y-8">
      <h1 className="text-3xl font-bold text-center">Tu Informe de Resultados</h1>

      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-6 right-6 bg-black bg-opacity-75 text-white px-4 py-2 rounded shadow-lg">
          {toast}
        </div>
      )}

      {/* ———————————— */}
      {/* 4️⃣ Sección de Análisis de CV */}
      {/* ———————————— */}
      {cvAnalysis ? (
        <div className="bg-gray-50 p-4 rounded shadow">
          <h2 className="text-2xl font-semibold mb-2">Análisis de tu CV</h2>
          <p className="mb-4">
            Puntuación global: <strong>{cvAnalysis.score}%</strong>
          </p>

          <h3 className="font-medium">Fortalezas</h3>
          <ul className="list-disc ml-6 mb-4">
            {cvAnalysis.strengths.map(str => (
              <li key={str}>{str}</li>
            ))}
          </ul>

          <h3 className="font-medium">Áreas a mejorar</h3>
          <ul className="list-disc ml-6">
            {cvAnalysis.weaknesses.map(w => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="text-center text-gray-500">
          No hay análisis de CV disponible.
        </p>
      )}

      {/* ———————————— */}
      {/* 5️⃣ Sección de Minijuegos */}
      {/* ———————————— */}
      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-2xl font-semibold mb-2">Minijuegos</h2>

        <h3 className="font-medium">Puntos fuertes</h3>
        {fortalezas.length > 0 ? (
          <ul className="list-disc ml-6 mb-4">
            {fortalezas.map(d => (
              <li key={d.subject}>
                {d.subject}: {d.dA}%
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 mb-4">No hay puntos fuertes aún.</p>
        )}

        <h3 className="font-medium">Áreas a mejorar</h3>
        {areasMejorar.length > 0 ? (
          <ul className="list-disc ml-6">
            {areasMejorar.map(d => (
              <li key={d.subject}>
                {d.subject}: {d.dA}%
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">
            ¡Perfecto! Todos los minijuegos completados.
          </p>
        )}
      </div>

      {/* ———————————— */}
      {/* 6️⃣ Botones de acción */}
      {/* ———————————— */}
      <div className="flex flex-col md:flex-row justify-center gap-4">
        <button
          onClick={() => navigate('/games')}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
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
          {loading ? 'Generando…' : 'Descargar Informe'}
        </button>
      </div>
    </section>
  )
}
