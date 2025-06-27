// src/pages/GameDashboardPage.tsx
import React from 'react'
import { useSelector } from 'react-redux'
import { Link } from 'react-router-dom'

// Lista de minijuegos con nombre, habilidad blanda y día asociado
const GAMES = [
  {
    id: '1',
    title: 'Primera llamada del día',
    skill: 'Toma de decisiones',
    icon: '/icons/game1.svg',
    day: 'Lunes',
  },
  {
    id: '2',
    title: 'Algo no cuadra',
    skill: 'Resolución de problemas',
    icon: '/icons/game2.svg',
    day: 'Martes',
  },
  {
    id: '3',
    title: 'El envío urgente',
    skill: 'Trabajo en equipo',
    icon: '/icons/game3.svg',
    day: 'Miércoles',
  },
  {
    id: '4',
    title: 'Día de tensiones',
    skill: 'Gestión emocional',
    icon: '/icons/game4.svg',
    day: 'Jueves',
  },
  {
    id: '5',
    title: 'Reunión sorpresa',
    skill: 'Comunicación',
    icon: '/icons/game5.svg',
    day: 'Viernes',
  },
  // JUEGOS EXTRAS – Solo se desbloquean al completar Lunes a Viernes
  {
    id: '6',
    title: '¿Y esto para qué sirve?',
    skill: 'Curiosidad y aprendizaje continuo',
    icon: '/icons/game6.svg',
    day: 'Extra',
  },
  {
    id: '7',
    title: 'La caja rota',
    skill: 'Creatividad',
    icon: '/icons/game7.svg',
    day: 'Extra',
  },
  {
    id: '8',
    title: 'Ruta equivocada',
    skill: 'Flexibilidad',
    icon: '/icons/game8.svg',
    day: 'Extra',
  },
  {
    id: '9',
    title: 'Pedido duplicado',
    skill: 'Pensamiento analítico',
    icon: '/icons/game9.svg',
    day: 'Extra',
  },
  {
    id: '10',
    title: 'Sistema nuevo',
    skill: 'Autonomía',
    icon: '/icons/game10.svg',
    day: 'Extra',
  },
]

export default function GameDashboardPage() {
  const completedGames: string[] = useSelector(
    (state: any) => state.progress.completedGames || []
  )
  const unlockedGames: number = useSelector(
    (state: any) => state.personal.unlockedGames || 1
  )

  // Filtramos los juegos por día laboral y extra
  const workDays = GAMES.slice(0, 5)
  const extraGames = GAMES.slice(5)

  // Determinamos si los extras están disponibles
  const allWorkDaysCompleted = workDays.every(game =>
    completedGames.includes(game.id)
  )

  // Mostramos solo los juegos básicos + extras si ya completó Lunes a Viernes
  const availableGames = [
    ...workDays,
    ...(allWorkDaysCompleted ? extraGames : []),
  ]

  // Si completó todos los juegos → medallero final
  if (completedGames.length >= GAMES.length) {
    return (
      <div className="p-6 text-center">
        <h1 className="text-3xl font-bold mb-6">🎉 ¡Enhorabuena!</h1>
        <p className="mb-6">
          Has completado los 10 minijuegos. Ahora sube tu CV para generar tu informe final.
        </p>

        {/* Medallero */}
        <div className="grid grid-cols-5 gap-6 max-w-screen-lg mx-auto mb-8">
          {GAMES.map((game) => {
            const completed = completedGames.includes(game.id)
            return (
              <div key={game.id} className="flex flex-col items-center">
                <img
                  src={completed ? game.icon : '/icons/locked.svg'}
                  alt={game.title}
                  className="w-16 h-16 mb-2"
                  onError={(e) => {
                    e.currentTarget.src = '/icons/fallback.svg'
                  }}
                />
                <span className="text-sm">{game.title}</span>
              </div>
            )
          })}
        </div>

        {/* Botón para subir CV */}
        <Link
          to="/upload-cv"
          className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Subir tu CV
        </Link>
      </div>
    )
  }

  // Muestra los juegos disponibles
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Minijuegos</h1>

      {/* Progreso visual */}
      <div className="mb-6 text-center">
        <p className="text-gray-600">
          Has completado{' '}
          <span className="font-semibold">{completedGames.length}</span> de{' '}
          <span className="font-semibold">{availableGames.length}</span> minijuegos disponibles
        </p>
        <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
          <div
            className="bg-green-500 h-2.5 rounded-full"
            style={{
              width: `${(completedGames.length / availableGames.length) * 100}%`,
            }}
          ></div>
        </div>
      </div>

      {/* Juegos pendientes */}
      <div className="grid grid-cols-5 gap-6 max-w-screen-lg mx-auto">
        {availableGames.map((game) => {
          const isCompleted = completedGames.includes(game.id)
          const isUnlocked = Number(game.id) <= unlockedGames

          return (
            <div
              key={game.id}
              className={`flex flex-col items-center p-4 border rounded-lg transition-all ${
                isCompleted
                  ? 'opacity-60 cursor-not-allowed'
                  : isUnlocked
                  ? 'hover:bg-gray-50 cursor-pointer'
                  : 'opacity-40 cursor-default'
              }`}
            >
              <Link
                to={isUnlocked ? `/games/${game.id}` : '#'}
                className="w-full h-full"
                onClick={(e) => !isUnlocked && e.preventDefault()}
              >
                <img
                  src={isCompleted ? game.icon : '/icons/unlocked-game.svg'}
                  alt={game.title}
                  className="w-12 h-12 mb-2 mx-auto"
                  onError={(e) => {
                    e.currentTarget.src = '/icons/fallback.svg'
                  }}
                />
                <span className="block font-medium text-center">{game.title}</span>
                <span className="text-xs text-gray-500 text-center">{game.skill}</span>
              </Link>
            </div>
          )
        })}
      </div>
    </div>
  )
}