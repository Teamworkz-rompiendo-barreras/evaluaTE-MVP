import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GameScene, GameOption } from '../../types/game';

interface ChoiceSceneProps {
  scene: GameScene;
  onComplete: (selectedOptionId: string) => void;
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

const ChoiceScene: React.FC<ChoiceSceneProps> = ({
  scene,
  onComplete,
  accessibility
}) => {
  const navigate = useNavigate();
  const [_selectedOption, setSelectedOption] = useState<string | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);

  const handleOptionSelect = (optionId: string) => {
    setSelectedOption(optionId);
    setShowFeedback(true);

    // Si es la opción "volver-menu", primero ejecuta onComplete y luego navega
    if (optionId === 'volver-menu') {
      onComplete(optionId);
      setTimeout(() => {
        navigate('/games');
      }, 500); // Pequeño delay para asegurar que Redux se actualiza
      return;
    }

    setTimeout(() => {
      onComplete(optionId);
    }, 2000);
  };

  const handleAudioPlay = (option: GameOption) => {
    if (accessibility.audioEnabled && option.text) {
      // Aquí se implementaría la funcionalidad de audio
      const utterance = new SpeechSynthesisUtterance(option.text);
      utterance.lang = 'es-ES';
      speechSynthesis.speak(utterance);
    }
  };

  return (
    <div className="choice-scene">
      <div className="options-container space-y-4">
        {(scene.options || []).map((option: GameOption) => (
          <div
            key={option.id}
            className={`option-card p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
              _selectedOption === option.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-blue-300 hover:bg-gray-50'
            } ${
              accessibility.contrastLevel === 'high'
                ? 'bg-white border-black'
                : ''
            }`}
            onClick={() => handleOptionSelect(option.id)}
            onMouseEnter={() => {
              if (accessibility.audioEnabled) {
                handleAudioPlay(option);
              }
            }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {option.icon && (
                  <span className="text-2xl">{option.icon}</span>
                )}
                <span 
                  className="text-lg font-medium"
                  style={{ fontSize: `${accessibility.fontScale}%` }}
                >
                  {option.text}
                </span>
              </div>
              
              {accessibility.audioEnabled && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleAudioPlay(option);
                  }}
                  className="p-2 rounded-full bg-gray-200 hover:bg-gray-300"
                  aria-label="Escuchar opción"
                >
                  🔊
                </button>
              )}
            </div>

            {/* Feedback que aparece cuando se selecciona */}
            {showFeedback && _selectedOption === option.id && option.feedback && (
              <div className="mt-3 p-3 bg-green-100 border border-green-300 rounded">
                <p className="text-green-800">{option.feedback}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Instrucciones de accesibilidad */}
      {accessibility.visualHelp && (
        <div className="mt-4 p-3 bg-blue-100 border border-blue-300 rounded">
          <p className="text-blue-800 text-sm">
            💡 Selecciona la opción que mejor represente lo que harías en esta situación.
          </p>
        </div>
      )}
    </div>
  );
};

export default ChoiceScene; 