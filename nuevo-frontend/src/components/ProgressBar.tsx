// src/components/ProgressBar.tsx
import React from 'react'

interface Props {
  step: number
  total: number
  label?: string // Etiqueta opcional, ej: "Progreso", "Minijuegos"
}

export default function ProgressBar({ step, total, label = 'Minijuego' }: Props) {
  const percent = Math.min(100, Math.round((step / total) * 100))
  const completedText = `${step} de ${total} ${label}${total > 1 ? 's' : ''} completados`

  return (
    <div className="w-full mb-4">
      {/* Texto descriptivo */}
      {percent > 0 && (
        <div className="text-sm text-center mb-2 font-medium text-gray-700">
          {completedText}
        </div>
      )}

      {/* Barra de progreso */}
      <div className="bg-gray-200 rounded-full h-2.5 w-full">
        <div
          className="bg-gradient-to-r from-blue-600 to-indigo-500 h-2.5 rounded-full transition-all duration-300 ease-in-out"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
}