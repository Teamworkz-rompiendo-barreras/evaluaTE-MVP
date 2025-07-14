// src/components/AccessibilitySettings.tsx
import { FC } from "react";
import { useAccessibility } from "../hooks/useAccessibility";

export const AccessibilitySettings: FC = () => {
  const { contrastLevel, fontScale, toggleContrast, setFontScale } =
    useAccessibility();

  return (
    <div
      role="region"
      aria-label="Ajustes de accesibilidad"
      className="fixed bottom-4 right-4 p-3 bg-white dark:bg-gray-800 rounded-lg shadow-lg z-50 flex flex-col items-center gap-2"
    >
      {/* Toggle de alto contraste */}
      <button
        onClick={toggleContrast}
        className="p-2 border rounded"
        aria-pressed={contrastLevel !== 'normal'}
      >
        {contrastLevel === 'normal' ? "🌙 Modo normal" : "⚡ Alto contraste"}
      </button>

      {/* Slider de tamaño de fuente */}
      <label className="flex flex-col items-center text-sm">
        Tamaño de fuente: {fontScale}%
        <input
          type="range"
          min={80}
          max={150}
          step={10}
          value={fontScale}
          onChange={(e) => setFontScale(Number(e.target.value))}
          className="mt-1"
          aria-valuemin={80}
          aria-valuemax={150}
          aria-valuenow={fontScale}
        />
      </label>
    </div>
  );
};