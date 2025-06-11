// src/components/ProgressBar.tsx
import React from 'react'

interface Props {
  step: number
  total: number
}

export default function ProgressBar({ step, total }: Props) {
  const percent = Math.round((step / total) * 100)
  return (
    <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
      <div
        className="bg-blue-600 h-2 rounded-full"
        style={{ width: `${percent}%` }}
      />
    </div>
  )
}
