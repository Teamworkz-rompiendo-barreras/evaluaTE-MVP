import toast from 'react-hot-toast'
import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useGetSceneQuery } from '../features/games/scenesApi'
import { useGameController } from '../features/games/useGameController'
import { useAppDispatch } from '../app/hooks'
import { markComplete } from '../app/store'

// Lista de habilidades (10 minijuegos)
const skills = [
  "Comunicación","Trabajo en equipo","Autonomía","Gestión del tiempo","Flexibilidad",
  "Pensamiento crítico","Resolución de problemas","Creatividad","Empatía","Liderazgo",
]

export default function GameScenePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()

  const {
    data: scene,
    isLoading,
    isError
  } = useGetSceneQuery(id ?? '', { skip: !id })

  const stepsCount = scene?.steps.length ?? 0
  const { currentStep, timeLeft, goNext, goPrev } = useGameController(stepsCount)

  if (isLoading) {
    return <main className="flex items-center justify-center min-h-screen"><p>Cargando escena…</p></main>
  }
  if (isError || !scene) {
    return (
      <main className="flex flex-col items-center justify-center min-h-screen gap-6">
        <p className="text-lg font-semibold text-red-600">Error al cargar la escena.</p>
        <p>Este minijuego aún no está disponible. Vuelve al menú de minijuegos.</p>
        <button className="py-2 px-4 bg-blue-600 text-white rounded" onClick={() => navigate('/games')}>
          Volver al menú de minijuegos
        </button>
      </main>
    )
  }

  const gameNum = Number(id)
  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4">
      <h2 className="text-xl font-semibold mb-4">{scene.title}</h2>
      <div className="mb-4">Tiempo restante: {timeLeft}s</div>
      <div className="mb-6 max-w-lg text-center"><p>{scene.steps[currentStep].text}</p></div>
      <div className="flex gap-4">
        <button onClick={goPrev} disabled={currentStep===0} className="py-2 px-4 bg-gray-300 text-gray-700 rounded disabled:opacity-50">
          Atrás
        </button>
        {currentStep < stepsCount - 1 ? (
          <button onClick={goNext} className="py-2 px-4 bg-blue-600 text-white rounded">
            Siguiente
          </button>
        ) : (
          <button
            onClick={() => {
              dispatch(markComplete(gameNum))
              toast.success(`¡Has completado "${scene.title}"!`)
                // Si no quedan más juegos, al medallero; si no, al siguiente juego
            const nextGame = gameNum + 1
            if (nextGame <= skills.length) {
             navigate(`/games/${nextGame}`)
            } else {
             navigate('/games')
            }
            }}
            className="py-2 px-4 bg-green-600 text-white rounded"
          >
            Finalizar
          </button>
        )}
      </div>
    </main>
  )
}
