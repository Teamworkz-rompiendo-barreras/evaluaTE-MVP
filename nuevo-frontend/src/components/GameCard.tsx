// src/components/GameCard.tsx
import React, { FC } from 'react'
import { Link } from 'react-router-dom'

interface GameCardProps {
  id: number
  name: string
  locked: boolean
}

const GameCard: FC<GameCardProps> = ({ id, name, locked }) => {
  // El contenido visual
  const cardContent = (
    <div
      className={`flex flex-col items-center justify-center p-4 rounded-xl w-32 h-32
                  text-center border transition
                  ${locked ? 'opacity-40 cursor-not-allowed'
                            : 'hover:scale-105 bg-white shadow'}`}
    >
      <div className="text-4xl mb-2">{locked ? '🔒' : '🎮'}</div>
      <span className="text-sm font-medium">{name}</span>
    </div>
  )

  // Si está bloqueada, devolvemos un DIV con aria-disabled
  if (locked) {
    return <div aria-disabled="true">{cardContent}</div>
  }

  // Si no está bloqueada, devolvemos un Link
  return (
    <Link to={`/games/${id}`} aria-label={`Jugar ${name}`}>
      {cardContent}
    </Link>
  )
}

export default GameCard


