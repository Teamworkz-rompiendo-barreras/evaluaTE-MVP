// src/pages/GameDashboardPage.tsx
import React from 'react'
import { useSelector } from 'react-redux'
import { Link } from 'react-router-dom'

// Definimos la lista con rutas absolutas a /icons en public/
const GAMES = Array.from({ length: 10 }, (_, i) => {
  const id = String(i + 1)
  return {
    id,
    title: `Minijuego ${id}`,
    icon: `/icons/game${id}.svg`
  }
})

export default function GameDashboardPage() {
  const completedGames: string[] = useSelector(
    (state: any) => state.progress.completedGames || []
  )

  // Si completó los 10, mostramos medallero
  if (completedGames.length >= GAMES.length) {
    return (
      <div className="p-6 text-center">
        <h1 className="text-3xl font-bold mb-6">🎉 ¡Enhorabuena!</h1>
        <p className="mb-6">Has completado tu semana laboral. Aquí tu medallero:</p>
        <div className="grid grid-cols-2 gap-6 max-w-lg mx-auto mb-8">
          {GAMES.map((g) => (
            <div key={g.id} className="flex flex-col items-center">
              <img
                src={g.icon}
                alt={g.title}
                className="w-16 h-16 mb-2"
                onError={(e) => { e.currentTarget.src = '/icons/fallback.svg' }}
              />
              <span className="text-sm">{g.title}</span>
            </div>
          ))}
        </div>
        <Link
          to="/upload-cv"
          className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700"
        >
          Ver mi informe completo
        </Link>
      </div>
    )
  }

  // Si no, cinco y cinco en dos columnas, solo los pendientes
  const pending = GAMES.filter((g) => !completedGames.includes(g.id))

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Minijuegos</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {pending.map((g) => (
          <Link
            key={g.id}
            to={`/games/${g.id}`}
            className="flex items-center space-x-4 p-4 border rounded-lg hover:bg-gray-50"
          >
            <img
              src={g.icon}
              alt={g.title}
              className="w-12 h-12"
              onError={(e) => { e.currentTarget.src = '/icons/fallback.svg' }}
            />
            <span className="font-medium">{g.title}</span>
          </Link>
        ))}
      </div>
    </div>
  )
}
