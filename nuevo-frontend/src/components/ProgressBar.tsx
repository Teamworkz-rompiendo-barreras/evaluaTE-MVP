// src/components/ProgressBar.tsx
import React from 'react'

interface ProgressBarProps {
  current: number;
  total: number;
  label?: string;
  showPercentage?: boolean;
  color?: string;
  size?: 'sm' | 'md' | 'lg';
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

  return (
    <div className="w-full mb-4">
      {/* Texto descriptivo */}
      {showPercentage && percent > 0 && (
        <div className="text-sm text-center mb-2 font-medium text-gray-700 dark:text-gray-300">
          {completedText}
        </div>
      )}

      {/* Barra de progreso */}
      <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 w-full transition-colors">
        <div
          className={`bg-gradient-to-r from-${color}-600 to-${color}-500 dark:from-${color}-400 dark:to-${color}-300 h-2.5 rounded-full transition-all duration-300 ease-in-out`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
}

export default ProgressBar