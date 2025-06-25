import React from 'react'
import { useSelector } from 'react-redux'
import GameCard from '../components/GameCard'
import { RootState } from '../app/store' // Asegúrate de importar correctamente tu store

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
  "Liderazgo",
]

export default function GameDashboardPage() {
  // Saca el número de minijuegos desbloqueados del store de Redux
  const unlockedGames = useSelector((state: RootState) => state.personal.unlockedGames);

  return (
    <main className="min-h-screen p-6 flex flex-col items-center gap-6">
      <h1 className="text-2xl font-bold">Elige un minijuego</h1>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        {skills.map((skill, idx) => {
          const gameId = idx + 1  // IDs van de 1 a 10
          return (
            <GameCard
              key={gameId}
              id={gameId}
              name={skill}
              locked={gameId > unlockedGames}  // desbloqueados hasta el último jugado + 1
            />
          )
        })}
      </div>
    </main>
  )
}
