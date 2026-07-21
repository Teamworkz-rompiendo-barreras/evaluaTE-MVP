import React, { useState } from 'react';
import { GameScene, InteractiveArea } from '../../types/game';

interface VisualExplorationSceneProps {
  scene: GameScene;
  onComplete: (selectedOptionId?: string, additionalData?: unknown) => void;
  onHelpRequest: () => void;
  onAdaptation: (adaptation: string) => void;
  accessibility: {
    contrastLevel: 'normal' | 'high';
    fontScale: number;
    audioEnabled: boolean;
    visualHelp: boolean;
    timeExtensions: boolean;
  };
}

const VisualExplorationScene: React.FC<VisualExplorationSceneProps> = ({
  scene,
  onComplete,
  accessibility: _accessibility
}) => {
  const [exploredAreas, setExploredAreas] = useState<string[]>([]);
  const [selectedArea, setSelectedArea] = useState<string | null>(null);

  const visualConfig = scene.visualConfig;
  if (!visualConfig) return <div>Configuración visual no encontrada</div>;

  const handleAreaClick = (area: InteractiveArea) => {
    setSelectedArea(area.id);
    if (!exploredAreas.includes(area.id)) {
      setExploredAreas([...exploredAreas, area.id]);
    }

    // Si es modo exploración, continuar después de un tiempo
    if (visualConfig.explorationMode) {
      setTimeout(() => {
        onComplete(area.id, { 
          exploredAreas: [...exploredAreas, area.id],
          totalAreas: visualConfig.interactiveAreas.length 
        });
      }, 2000);
    }
  };

  return (
    <div className="visual-exploration-scene">
      {/* Imagen principal */}
      <div className="image-container mb-6 relative">
        <div 
          className="w-full h-64 bg-gray-200 rounded-lg relative overflow-hidden"
          style={{ 
            backgroundImage: visualConfig.imageUrl ? `url(${visualConfig.imageUrl})` : 'none',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        >
          {/* Áreas interactivas */}
          {(Array.isArray(visualConfig.interactiveAreas) ? visualConfig.interactiveAreas : []).map((area) => (
            <div
              key={area.id}
              onClick={() => handleAreaClick(area)}
              className={`absolute cursor-pointer border-2 border-transparent hover:border-blue-400 transition-colors ${
                exploredAreas.includes(area.id) ? 'border-green-400 bg-green-200 bg-opacity-30' : ''
              }`}
              style={{
                left: `${area.x}%`,
                top: `${area.y}%`,
                width: `${area.width}%`,
                height: `${area.height}%`
              }}
              title={area.feedback || `Área ${area.id}`}
            />
          ))}
        </div>
      </div>

      {/* Información de exploración */}
      {visualConfig.explorationMode && (
        <div className="exploration-info mb-4">
          <p className="text-center text-gray-600">
            Has explorado {exploredAreas.length} de {visualConfig.interactiveAreas.length} áreas
          </p>
          <div className="progress-bar mt-2 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(exploredAreas.length / visualConfig.interactiveAreas.length) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Feedback del área seleccionada */}
      {selectedArea && (
        <div className="selected-area-feedback p-4 bg-blue-100 border border-blue-300 rounded">
          <p className="text-blue-800">
            {visualConfig.interactiveAreas.find(a => a.id === selectedArea)?.feedback || 
             `Has seleccionado el área ${selectedArea}`}
          </p>
        </div>
      )}

      {/* Instrucciones */}
      <div className="instructions mt-4 p-3 bg-gray-100 rounded">
        <p className="text-sm text-gray-700">
          {visualConfig.explorationMode 
            ? 'Explora las diferentes áreas de la imagen haciendo clic en ellas.'
            : 'Haz clic en las áreas interactivas para obtener más información.'
          }
        </p>
      </div>
    </div>
  );
};

export default VisualExplorationScene; 