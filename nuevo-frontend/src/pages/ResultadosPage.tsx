// src/pages/ResultadosPage.tsx
import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppSelector } from '../app/hooks'

// Definimos el formato que usaremos internamente
interface AnalysisEntry {
  subject: string
  dA: number
}

export default function ResultadosPage() {
  const navigate = useNavigate()
  // Leemos el progreso de los minijuegos del store
  const completed = useAppSelector(state => state.progress.completed)

  // Creamos nuestro array de resultados a partir del objeto { [id]: boolean }
  const data: AnalysisEntry[] = Object.keys(completed).map(key => ({
    subject: `Minijuego ${key}`,
    dA: completed[Number(key)] ? 100 : 0
  }))

  const fortalezas   = data.filter(d => d.dA >= 75)
  const areasMejorar = data.filter(d => d.dA < 75)

  return (
    <section className="max-w-2xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold text-center">Tu Informe de Resultados</h1>

      <h2 className="text-xl font-semibold">Puntos fuertes</h2>
      <ul className="list-disc pl-5">
        {fortalezas.map(d => (
          <li key={d.subject}>
            {d.subject}: {d.dA}%
          </li>
        ))}
      </ul>

      <h2 className="text-xl font-semibold mt-6">Áreas a mejorar</h2>
      <ul className="list-disc pl-5">
        {areasMejorar.map(d => (
          <li key={d.subject}>
            {d.subject}: {d.dA}%
          </li>
        ))}
      </ul>

      <div className="text-center mt-8">
        <button
          onClick={() => navigate('/games')}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Volver al Dashboard
        </button>
      </div>
    </section>
  )
}
