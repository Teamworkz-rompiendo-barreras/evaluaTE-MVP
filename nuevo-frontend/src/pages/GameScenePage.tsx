import { useParams } from 'react-router-dom'
import { useGetSceneQuery } from '../features/games/scenesApi'
import { useGameController } from '../features/games/useGameController'

export default function GameScenePage() {
  // 1️⃣ Leemos el parámetro id de la URL
  const { id } = useParams<{ id: string }>()

  // 2️⃣ Llamamos al endpoint con RTK Query
  const { data: scene, isLoading, isError } = useGetSceneQuery(id!)
  
  // 3️⃣ Estado del juego: esperamos a que llegue scene para arrancar el hook
  const controller = scene
    ? useGameController(scene.steps.length)
    : null

  // 4️⃣ Gestión de estados de carga y error
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

  // 5️⃣ Una vez que tenemos scene y controller, renderizamos
  const { currentStep, timeLeft, goNext } = controller!

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4">
      <h2 className="text-xl font-semibold mb-4">{scene.title}</h2>

      {/* Temporizador */}
      <div className="mb-4">Tiempo restante: {timeLeft}s</div>

      {/* Paso actual */}
      <div className="mb-6">
        {/* Ajusta esto según la estructura de tus steps */}
        <p>{scene.steps[currentStep].text}</p>
      </div>

      {/* Botón de siguiente */}
      {currentStep < scene.steps.length - 1 ? (
        <button
          onClick={goNext}
          className="py-2 px-4 bg-blue-600 text-white rounded"
        >
          Siguiente
        </button>
      ) : (
        <p>Has completado este minijuego 🎉</p>
      )}
    </main>
  )
}

