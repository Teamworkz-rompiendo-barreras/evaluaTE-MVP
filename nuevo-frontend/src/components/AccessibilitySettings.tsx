// src/components/AccessibilitySettings.tsx
import { FC } from "react";
import { useAccessibility } from "../hooks/useAccessibility";

export const AccessibilitySettings: FC = () => {
  const { 
    contrastLevel, 
    fontScale, 
    fontFamily, 
    toggleContrast, 
    setFontScale, 
    setFontFamily 
  } = useAccessibility();

  return (
    <div
      role="region"
      aria-label="Ajustes de accesibilidad"
      className="fixed bottom-4 right-4 p-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg z-50 flex flex-col items-center gap-3 min-w-[280px]"
    >
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-2">
        Accesibilidad
      </h3>
      
      {/* Toggle de alto contraste */}
      <button
        onClick={toggleContrast}
        className="w-full p-3 border-2 border-gray-300 rounded-lg hover:border-primary transition-colors"
        aria-pressed={contrastLevel !== 'normal'}
      >
        {contrastLevel === 'normal' ? "🌙 Modo normal" : "⚡ Alto contraste"}
      </button>

      {/* Selector de tipografía accesible */}
      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Tipografía:
        </label>
        <select
          value={fontFamily}
          onChange={(e) => setFontFamily(e.target.value)}
          className="w-full p-2 border-2 border-gray-300 rounded-lg focus:border-primary focus:outline-none"
          aria-label="Seleccionar tipografía accesible"
        >
          <option value="sans">📖 Estándar (Atkinson Hyperlegible)</option>
          <option value="dyslexic">🎯 Dislexia (OpenDyslexic)</option>
          <option value="readable">👁️ Alta legibilidad</option>
        </select>
      </div>

      {/* Slider de tamaño de fuente */}
      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Tamaño de fuente: {fontScale}%
        </label>
        <input
          type="range"
          min={80}
          max={200}
          step={10}
          value={fontScale}
          onChange={(e) => setFontScale(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          aria-valuemin={80}
          aria-valuemax={200}
          aria-valuenow={fontScale}
          aria-label="Ajustar tamaño de fuente"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>80%</span>
          <span>140%</span>
          <span>200%</span>
        </div>
      </div>

      {/* Información sobre accesibilidad cognitiva */}
      <div className="w-full p-3 bg-blue-50 dark:bg-blue-900 rounded-lg">
        <p className="text-xs text-blue-800 dark:text-blue-200">
          💡 <strong>Accesibilidad cognitiva:</strong> Estas opciones mejoran la legibilidad para personas con dislexia, TDAH y otras necesidades cognitivas.
        </p>
      </div>
    </div>
  );
};