// src/pages/GameDashboardPage.tsx
import React from 'react'
import { useSelector } from 'react-redux'
import { Link } from 'react-router-dom'

// Define aquí tu lista de minijuegos según tu doc de gamificación
const GAMES = [
  { id: '1', title: 'Minijuego 1', icon: '/icons/game1.svg' },
  { id: '2', title: 'Minijuego 2', icon: '/icons/game2.svg' },
  { id: '3', title: 'Minijuego 3', icon: '/icons/game3.svg' },
  { id: '4', title: 'Minijuego 4', icon: '/icons/game4.svg' },
  { id: '5', title: 'Minijuego 5', icon: '/icons/game5.svg' },
  { id: '6', title: 'Minijuego 6', icon: '/icons/game6.svg' },
  { id: '7', title: 'Minijuego 7', icon: '/icons/game7.svg' },
  { id: '8', title: 'Minijuego 8', icon: '/icons/game8.svg' },
  { id: '9', title: 'Minijuego 9', icon: '/icons/game9.svg' },
  { id: '10', title: 'Minijuego 10', icon: '/icons/game10.svg' },
]

export default function GameDashboardPage() {
  // Selector: array de ids completados
  const completedGames: string[] = useSelector(
    (state: any) => state.progress.completedGames || []
  )

  // Si ya ha completado todos los juegos
  if (completedGames.length >= GAMES.length) {
    return (
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">🎉 ¡Enhorabuena!</h1>
        <p className="mb-6">
          Has completado los 10 minijuegos. Aquí tienes tu medallero:
        </p>
        <div className="grid grid-cols-5 gap-4 mb-6">
          {GAMES.map((g) => (
            <div key={g.id} className="flex flex-col items-center">
              <img src={g.icon} alt={g.title} className="w-12 h-12" />
              <span className="text-sm mt-2">{g.title}</span>
            </div>
          ))}
        </div>
        <Link
          to="/upload-cv"
          className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
        >
          Ver mi informe completo
        </Link>
      </div>
    )
  }

  // Si quedan juegos por hacer
  const pending = GAMES.filter((g) => !completedGames.includes(g.id))

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Minijuegos</h1>
      <ul className="space-y-3">
        {pending.map((g) => (
          <li key={g.id}>
            <Link
              to={`/games/${g.id}`}
              className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50"
            >
              <img src={g.icon} alt={g.title} className="w-10 h-10" />
              <span>{g.title}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
