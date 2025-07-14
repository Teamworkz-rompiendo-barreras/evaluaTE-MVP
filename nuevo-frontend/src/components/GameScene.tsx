import React, { useState } from 'react';
import { GameScene as GameSceneType, GameLog } from '../types/game';
import ChoiceScene from './scenes/ChoiceScene';
import DragDropScene from './scenes/DragDropScene';
import AudioScene from './scenes/AudioScene';
import VisualExplorationScene from './scenes/VisualExplorationScene';

interface GameSceneProps {
  scene: GameSceneType;
  onSceneComplete: (log: GameLog) => void;
  onNextScene: (sceneId: string) => void;
  accessibility: {
    contrastLevel: 'normal' | 'high';
    fontScale: number;
    audioEnabled: boolean;
    visualHelp: boolean;
    timeExtensions: boolean;
  };
}

const GameScene: React.FC<GameSceneProps> = ({
  scene,
  onSceneComplete,
  onNextScene,
  accessibility
}) => {
  console.log('🎮 GameScene - Renderizando escena:', scene.id, scene.title);
  const [startTime] = useState(Date.now());
  const [helpUsed, setHelpUsed] = useState(false);
  const [adaptations, setAdaptations] = useState<string[]>([]);

  const handleSceneComplete = (selectedOptionId?: string) => {
    const timeSpent = Date.now() - startTime;
    
    const gameLog: GameLog = {
      sceneId: scene.id,
      selectedOptionId,
      timeSpent,
      helpUsed,
      adaptations,
      timestamp: new Date()
    };

    onSceneComplete(gameLog);

    // Determinar la siguiente escena
    if (selectedOptionId) {
      const selectedOption = scene.options?.find(opt => opt.id === selectedOptionId);
      if (selectedOption?.nextSceneId) {
        onNextScene(selectedOption.nextSceneId);
      } else if (scene.nextSceneId) {
        onNextScene(scene.nextSceneId);
      }
    } else if (scene.nextSceneId) {
      onNextScene(scene.nextSceneId);
    }
  };

  const handleHelpRequest = () => {
    setHelpUsed(true);
    setAdaptations(prev => [...prev, 'help_requested']);
  };

  const handleAdaptation = (adaptation: string) => {
    setAdaptations(prev => [...prev, adaptation]);
  };

  const renderSceneContent = () => {
    const commonProps = {
      scene,
      onComplete: handleSceneComplete,
      onHelpRequest: handleHelpRequest,
      onAdaptation: handleAdaptation,
      accessibility
    };

    switch (scene.type) {
      case 'choice':
        return <ChoiceScene {...commonProps} />;
      case 'drag-drop':
        return <DragDropScene {...commonProps} />;
      case 'audio':
        return <AudioScene {...commonProps} />;
      case 'visual-exploration':
        return <VisualExplorationScene {...commonProps} />;
      default:
        return <div>Escena no soportada</div>;
    }
  };

  return (
    <div 
      className={`game-scene p-6 rounded-lg shadow-lg ${
        accessibility.contrastLevel === 'high' 
          ? 'bg-white text-black border-2 border-black' 
          : 'bg-gray-50 text-gray-800'
      }`}
      style={{ fontSize: `${accessibility.fontScale}%` }}
    >
      {/* Título de la escena */}
      <h2 className="text-2xl font-bold mb-4 text-center">
        {scene.title}
      </h2>

      {/* Descripción */}
      <div className="mb-6 text-center">
        <p className="text-lg leading-relaxed">
          {scene.description}
        </p>
      </div>

      {/* Contenido de la escena */}
      <div className="scene-content">
        {renderSceneContent()}
      </div>

      {/* Botón de ayuda */}
      {scene.adaptiveHelp && (
        <div className="mt-4 text-center">
          <button
            onClick={handleHelpRequest}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            disabled={helpUsed}
          >
            {helpUsed ? 'Ayuda ya utilizada' : '¿Necesitas ayuda?'}
          </button>
        </div>
      )}

      {/* Indicador de tiempo (si hay límite) */}
      {scene.timeLimit && (
        <div className="mt-4 text-center text-sm text-gray-600">
          Tiempo restante: {scene.timeLimit}s
        </div>
      )}
    </div>
  );
};

export default GameScene; 