import React from 'react';
import { Game } from '../types/game';

interface GameCardProps {
  game: Game;
  isUnlocked: boolean;
  isCurrent: boolean;
  isCompleted: boolean;
  onClick?: () => void;
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
  isCompleted,
  onClick,
  accessibility
}) => {
  const getCardClasses = () => {
    let baseClasses = 'relative p-4 rounded-lg border-2 transition-all duration-300 cursor-pointer transition-colors';

    if (isCompleted) {
      baseClasses += ' bg-green-50 border-green-300 dark:bg-emerald-900/20 dark:border-emerald-600';
    } else if (isUnlocked) {
      baseClasses += ' bg-white border-gray-300 hover:border-blue-400 hover:shadow-lg dark:bg-slate-800 dark:border-slate-600';
    } else if (isCurrent) {
      baseClasses += ' bg-white border-gray-300 hover:border-blue-400 hover:shadow-lg dark:bg-slate-800 dark:border-slate-600';
    } else {
      baseClasses += ' bg-gray-100 border-gray-200 opacity-70 cursor-not-allowed dark:bg-slate-800/60 dark:border-slate-700';
    }

    if (accessibility.contrastLevel === 'high') {
      baseClasses += ' border-black bg-white dark:bg-black dark:border-white';
    }

    return baseClasses;
  };

  const getStatusIcon = () => {
    if (isCompleted) {
      return '✅';
    } else if (isUnlocked || isCurrent) {
      return '🎯';
    } else {
      return '🔒';
    }
  };

  const getStatusText = () => {
    if (isCompleted) {
      return 'Completado';
    } else if (isUnlocked || isCurrent) {
      return 'Disponible';
    } else {
      return 'Bloqueado';
    }
  };

  const handleClick = () => {
    if (onClick && (isUnlocked || isCurrent)) {
      onClick();
    }
  };

  return (
    <div
      className={`game-card ${getCardClasses()}`}
      style={{ fontSize: `${accessibility.fontScale}%` }}
      onClick={handleClick}
    >
      {/* Estado del juego */}
      <div className="absolute top-2 right-2">
        <span className="text-lg">{getStatusIcon()}</span>
      </div>

      {/* Icono del juego */}
      <div className="text-center mb-3">
        <div 
          className="text-4xl mb-2"
          style={{ color: isCompleted ? '#10B981' : game.color }}
        >
          {game.icon}
        </div>
      </div>

      {/* Información del juego */}
      <div className="text-center">
        <h3 className="font-semibold text-sm mb-1 line-clamp-2 text-gray-900 dark:text-gray-100">
          {game.title}
        </h3>
        <p className="text-xs text-gray-600 dark:text-gray-300 mb-2">
          {game.subtitle}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
          {game.day}
        </p>
        <span className="text-xs px-2 py-1 rounded-full bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-100">
          {getStatusText()}
        </span>
      </div>

      {/* Indicador de progreso si está completado */}
      {isCompleted && (
        <div className="mt-3">
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1 transition-colors">
            <div className="bg-green-500 dark:bg-green-400 h-1 rounded-full" style={{ width: '100%' }} />
          </div>
        </div>
      )}
    </div>
  );
};

export default GameCard;
