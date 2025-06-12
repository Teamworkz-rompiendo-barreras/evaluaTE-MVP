// src/components/ProtectedRoute.tsx
import React, { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAppSelector } from '../app/hooks'

interface ProtectedRouteProps {
  children: ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const location = useLocation()

  // 1) ¿Registro mínimo?
  const { firstName, jobPreferences } = useAppSelector(s => s.personal)
  const isRegistered = Boolean(firstName.trim() && jobPreferences.trim())

  // 2) ¿Algún juego desbloqueado?
  const completed = useAppSelector(s => s.progress.completed)
  const hasProgress = completed && Object.keys(completed).length > 0

  if (!isRegistered || !hasProgress) {
    return (
      <Navigate
        to="/register/contact"
        state={{ from: location }}
        replace
      />
    )
  }

  return <>{children}</>
}
