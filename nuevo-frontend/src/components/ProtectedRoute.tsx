import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAppSelector } from '../app/hooks'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const location = useLocation()
  const completed = useAppSelector(s => s.progress.completed)

  // Si no hay progreso (registro no completado), redirige al paso 1
  if (!completed || Object.keys(completed).length === 0) {
    return <Navigate to="/register/contact" state={{ from: location }} replace />
  }

  return <>{children}</>
}
