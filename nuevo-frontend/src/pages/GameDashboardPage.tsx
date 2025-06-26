import React from 'react'
import { useSelector } from 'react-redux'
import GameCard from '../components/GameCard'
import { RootState } from '../app/store'
import { useNavigate } from 'react-router-dom'

const skills = [
  "Comunicación","Trabajo en equipo","Autonomía","Gestión del tiempo","Flexibilidad",
  "Pensamiento crítico","Resolución de problemas","Creatividad","Empatía","Liderazgo",
]

export default function GameDashboardPage() {
  const navigate = useNavigate()
  const completed = useSelector((state: RootState) => state.progress.completed)
  // Último completado, o 0
  const last = Math.max(0, ...Object.keys(completed).map(Number))
  // Próximo desbloqueado
  const unlocked = Math.min(last+1, skills.length)

  return (
    <main className="min-h-screen p-6 flex flex-col items-center gap-6">
      <h1 className="text-2xl font-bold">Elige un minijuego</h1>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        {skills.map((skill, i) => {
          const id = i+1
          const done = !!completed[id]
          const locked = done || id>unlocked
          return (
            <GameCard key={id} id={id} name={skill} locked={locked} completed={done}/>
          )
        })}
      </div>
      {Object.keys(completed).length === skills.length && (
        <button className="mt-8 py-2 px-4 bg-green-600 text-white rounded" onClick={() => navigate('/upload-cv')}>
          Avanzar a subir CV
        </button>
      )}
    </main>
  )
}

