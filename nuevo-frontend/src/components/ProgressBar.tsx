// src/components/ProgressBar.tsx
import React from 'react'

const COLOR_MAP: Record<string, { from: string; to: string }> = {
  blue:   { from: '#2563eb', to: '#3b82f6' },
  green:  { from: '#16a34a', to: '#22c55e' },
  purple: { from: '#7c3aed', to: '#a855f7' },
  red:    { from: '#dc2626', to: '#ef4444' },
  yellow: { from: '#ca8a04', to: '#eab308' },
  orange: { from: '#ea580c', to: '#f97316' },
}

interface ProgressBarProps {
  current: number;
  total: number;
  label?: string;
  showPercentage?: boolean;
  color?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  current,
  total,
  label,
  showPercentage = true,
  color = 'blue'
}) => {
  const percent = Math.min(100, Math.round((current / total) * 100))
  const noun = (label && label.trim()) ? label.trim() : 'paso'
  const completedText = `${current} de ${total} ${noun}${total > 1 && !noun.endsWith('s') ? 's' : ''} completados`
  const colors = COLOR_MAP[color] ?? COLOR_MAP['blue']!

  return (
    <div className="w-full mb-4">
      {showPercentage && percent > 0 && (
        <div className="text-sm text-center mb-2 font-medium text-gray-700 dark:text-gray-300">
          {completedText}
        </div>
      )}

      <div
        role="progressbar"
        aria-valuenow={percent}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || 'Progreso del juego'}
        aria-valuetext={completedText}
        className="bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 w-full transition-colors"
      >
        <div
          className="h-2.5 rounded-full transition-all duration-300 ease-in-out"
          style={{
            width: `${percent}%`,
            background: `linear-gradient(to right, ${colors.from}, ${colors.to})`,
          }}
        />
      </div>
    </div>
  )
}

export default ProgressBar