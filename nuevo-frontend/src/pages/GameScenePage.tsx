// src/pages/GameScenePage.tsx
import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useGetSceneQuery } from '../features/games/scenesApi'
import { useGameController } from '../features/games/useGameController'
import { useAppDispatch } from '../app/hooks'
import { markComplete } from '../app/store'
import { useDispatch } from 'react-redux'
import { unlockNextGame } from '../features/personal/personalSlice'

export default function GameScenePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()

  // 1️⃣ Traemos la escena con RTK Query, y la pedimos solo si tenemos un id
  const {
    data: scene,
    isLoading,
    isError
  } = useGetSceneQuery(id ?? '', {
    // no lanzamos la petición si id es undefined
    skip: !id
  })

  // 2️⃣ Inicializamos el controlador con el número de pasos
  const stepsCount = scene?.steps.length ?? 0
  const {
    currentStep,
    timeLeft,
    goNext,
    goPrev
  } = useGameController(stepsCount)

  // 3️⃣ Estados de carga / error
  if (isLoading) {
    return (
      <main className="flex items-center justify-center min-h-screen">
        <p>Cargando escena…</p>
      </main>
    )
  }
  if (isError || !scene) {
    return (
      <main className="flex items-center justify-center min-h-screen">
        <p>Error al cargar la escena.</p>
      </main>
    )
  }

  // 4️⃣ Render final
  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4">
      {/* Título de la escena */}
      <h2 className="text-xl font-semibold mb-4">{scene.title}</h2>

      {/* Temporizador */}
      <div className="mb-4">Tiempo restante: {timeLeft}s</div>

      {/* Texto del paso actual */}
      <div className="mb-6 max-w-lg text-center">
        <p>{scene.steps[currentStep].text}</p>
      </div>

      {/* Controles */}
      <div className="flex gap-4">
        {/* Atrás */}
        <button
          onClick={goPrev}
          disabled={currentStep === 0}
          className="py-2 px-4 bg-gray-300 text-gray-700 rounded disabled:opacity-50"
        >
          Atrás
        </button>

        {/* Siguiente o Finalizar */}
        {currentStep < stepsCount - 1 ? (
          <button
            onClick={goNext}
            className="py-2 px-4 bg-blue-600 text-white rounded"
          >
            Siguiente
          </button>
        ) : (
          <button
            onClick={() => {
              // 1) Marcamos completado el minijuego actual
              dispatch(markComplete(Number(id)))
              // 2) Redirigimos de vuelta al dashboard
              navigate('/games')
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
