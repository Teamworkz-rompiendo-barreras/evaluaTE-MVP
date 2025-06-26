import React, { FC } from 'react';
import { Link } from 'react-router-dom';

interface GameCardProps {
  id: number;
  name: string;
  locked: boolean;
  completed: boolean;
}

const GameCard: FC<GameCardProps> = ({ id, name, locked, completed }) => {
  const dataCy = `game-card-${id}`;
  const ariaDisabled = locked ? 'true' : 'false';
  const commonClasses =
    'flex flex-col items-center justify-center p-4 rounded-xl w-32 h-32 text-center border transition';

  const content = (
    <div
      data-cy={dataCy}
      aria-disabled={ariaDisabled}
      className={
        locked
          ? `${commonClasses} opacity-40 cursor-not-allowed`
          : `${commonClasses} hover:scale-105 bg-white shadow`
      }
    >
      <div className="text-4xl mb-2">{locked ? '🔒' : completed ? '✔️' : '🎮'}</div>
      <span className="text-sm font-medium">
        {name}
        {completed && (
          <span className="ml-2 text-green-600 font-bold" title="Minijuego completado">
          </span>
        )}
      </span>
    </div>
  );

  // Si está bloqueado, devolvemos un DIV (no clicable)
  if (locked) {
    return content;
  }

  // Si está desbloqueado, devolvemos un Link envolviendo ese mismo DIV
  return (
    <Link to={`/games/${id}`} aria-label={`Jugar ${name}`} data-cy={dataCy} aria-disabled={ariaDisabled}>
      {content}
    </Link>
  );
};

export default GameCard;
