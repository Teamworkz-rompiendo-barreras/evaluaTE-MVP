import React from 'react'
import { useSelector } from 'react-redux'
import GameCard from '../components/GameCard'
import { RootState } from '../app/store'
import { useNavigate } from 'react-router-dom'

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
  const navigate = useNavigate();
  const completed = useSelector((state: RootState) => state.progress.completed);

  // Calcula el ID del siguiente minijuego que debe desbloquearse
  const lastCompletedId = Math.max(0, ...Object.keys(completed).map(Number));
  const unlockedGames = Math.min(lastCompletedId + 1, skills.length);

  return (
    <main className="min-h-screen p-6 flex flex-col items-center gap-6">
      <h1 className="text-2xl font-bold">Elige un minijuego</h1>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        {skills.map((skill, idx) => {
          const gameId = idx + 1;
          const isCompleted = !!completed[gameId];
          // BLOQUEA SI YA ESTÁ COMPLETADO O SI NO ES EL SIGUIENTE DESBLOQUEADO
          const locked = isCompleted || gameId > unlockedGames;
          return (
            <GameCard
              key={gameId}
              id={gameId}
              name={skill}
              locked={locked}
              completed={isCompleted}
            />
          )
        })}
      </div>

      {/* Botón para avanzar a subir CV si están todos hechos */}
      {Object.keys(completed).length === skills.length && (
        <button
          className="mt-8 py-2 px-4 bg-green-600 text-white rounded"
          onClick={() => navigate('/upload-cv')}
        >
          Avanzar a subir CV
        </button>
      )}
    </main>
  )
}
