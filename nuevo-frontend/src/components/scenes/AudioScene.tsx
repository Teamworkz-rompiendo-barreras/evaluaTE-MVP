import React, { useState } from 'react';
import { GameScene } from '../../types/game';

interface AudioSceneProps {
  scene: GameScene;
  onComplete: (selectedOptionId?: string) => void;
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

const AudioScene: React.FC<AudioSceneProps> = ({
  scene,
  onComplete
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);

  const audioConfig = scene.audioConfig;
  if (!audioConfig) return <div>Configuración de audio no encontrada</div>;

  const handlePlayAudio = () => {
    setIsPlaying(true);
    // Aquí se implementaría la reproducción de audio real
    setTimeout(() => setIsPlaying(false), 3000); // Simulación
  };

  const handleAnswerSelect = (_questionId: string, optionId: string) => {
    setSelectedAnswer(optionId);
    setTimeout(() => {
      onComplete(optionId);
    }, 1000);
  };

  return (
    <div className="audio-scene">
      {/* Controles de audio */}
      <div className="audio-controls mb-6 text-center">
        <button
          onClick={handlePlayAudio}
          disabled={isPlaying}
          className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
        >
          {isPlaying ? 'Reproduciendo...' : '▶️ Reproducir audio'}
        </button>
        
        {audioConfig.transcript && (
          <div className="mt-4 p-4 bg-gray-100 rounded">
            <h4 className="font-semibold mb-2">Transcripción:</h4>
            <p className="text-sm">{audioConfig.transcript}</p>
          </div>
        )}
      </div>

      {/* Preguntas */}
      <div className="questions space-y-4">
        {audioConfig.questions.map((question) => (
          <div key={question.id} className="question-card p-4 border rounded">
            <h3 className="font-semibold mb-3">{question.question}</h3>
            <div className="options space-y-2">
              {question.options.map((option) => (
                <button
                  key={option.id}
                  onClick={() => handleAnswerSelect(question.id, option.id)}
                  disabled={selectedAnswer !== null}
                  className={`w-full p-3 text-left rounded border transition-colors ${
                    selectedAnswer === option.id
                      ? 'bg-blue-100 border-blue-300'
                      : 'bg-white border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {option.text}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AudioScene; 