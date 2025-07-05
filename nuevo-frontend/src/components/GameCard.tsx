import React from 'react';
import { Game } from '../types/game';

interface GameCardProps {
  game: Game;
  isUnlocked: boolean;
  isCurrent: boolean;
  accessibility: {
    contrastLevel: 'normal' | 'high';
    fontScale: number;
    audioEnabled: boolean;
    visualHelp: boolean;
    timeExtensions: boolean;
  };
}

const GameCard: React.FC<GameCardProps> = ({
  game,
  isUnlocked,
  isCurrent,
  accessibility
}) => {
  const getCardClasses = () => {
    let baseClasses = 'relative p-4 rounded-lg border-2 transition-all duration-300 cursor-pointer';
    
    if (isUnlocked) {
      baseClasses += ' bg-green-50 border-green-300 opacity-80';
    } else if (isCurrent) {
      baseClasses += ' bg-white border-gray-300 hover:border-blue-400 hover:shadow-lg';
    } else {
      baseClasses += ' bg-gray-100 border-gray-200 opacity-50 cursor-not-allowed';
    }

    if (accessibility.contrastLevel === 'high') {
      baseClasses += ' border-black bg-white';
    }

    return baseClasses;
  };

  const getStatusIcon = () => {
    if (isUnlocked) {
      return '✅';
    } else if (isCurrent) {
      return '🎯';
    } else {
      return '🔒';
    }
  };

  const getStatusText = () => {
    if (isUnlocked) {
      return 'Completado';
    } else if (isCurrent) {
      return 'Siguiente';
    } else {
      return 'Bloqueado';
    }
  };

  return (
    <div
      className={getCardClasses()}
      style={{ fontSize: `${accessibility.fontScale}%` }}
    >
      {/* Estado del juego */}
      <div className="absolute top-2 right-2">
        <span className="text-lg">{getStatusIcon()}</span>
      </div>

      {/* Icono del juego */}
      <div className="text-center mb-3">
        <div 
          className="text-4xl mb-2"
          style={{ color: isUnlocked ? '#10B981' : game.color }}
        >
          {game.icon}
        </div>
      </div>

      {/* Información del juego */}
      <div className="text-center">
        <h3 className="font-semibold text-sm mb-1 line-clamp-2">
          {game.title}
        </h3>
        <p className="text-xs text-gray-600 mb-2">
          {game.subtitle}
        </p>
        <p className="text-xs text-gray-500 mb-2">
          {game.day}
        </p>
        <span className="text-xs px-2 py-1 rounded-full bg-gray-200 text-gray-700">
          {getStatusText()}
        </span>
      </div>

      {/* Indicador de progreso si está completado */}
      {isUnlocked && (
        <div className="mt-3">
          <div className="w-full bg-gray-200 rounded-full h-1">
            <div className="bg-green-500 h-1 rounded-full" style={{ width: '100%' }} />
          </div>
        </div>
      )}
    </div>
  );
};

export default GameCard;
