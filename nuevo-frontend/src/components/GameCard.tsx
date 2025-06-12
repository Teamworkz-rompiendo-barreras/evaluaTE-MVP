// src/components/GameCard.tsx
import React, { FC } from 'react'
import { Link } from 'react-router-dom'

interface GameCardProps {
  id: number
  name: string
  locked: boolean
}

const GameCard: FC<GameCardProps> = ({ id, name, locked }) => {
  // Contenido visual de la tarjeta
  const cardContent = (
    <div
      data-cy={`game-card-${id}`}             // <-- selector para Cypress
      className={`flex flex-col items-center justify-center p-4 rounded-xl w-32 h-32
                  text-center border transition
                  ${locked ? 'opacity-40 cursor-not-allowed' 
                            : 'hover:scale-105 bg-white shadow'}`}
      aria-disabled={locked}                   // booleano en vez de string
    >
      <div className="text-4xl mb-2">
        {locked ? '🔒' : '🎮'}
      </div>
      <span className="text-sm font-medium">{name}</span>
    </div>
  )

  // Si está bloqueada, devolvemos solo el div (no es clicable)
  if (locked) {
    return cardContent
  }

  // Si no está bloqueada, envolvemos en Link
  return (
    <Link
      to={`/games/${id}`}
      aria-label={`Jugar ${name}`}
      className="no-underline"               // opcional, para eliminar subrayado
    >
      {cardContent}
    </Link>
  )
}

export default GameCard



