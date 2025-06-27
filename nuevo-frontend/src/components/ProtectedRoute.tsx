// src/components/ProtectedRoute.tsx
import React from 'react'
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'

interface Props {
  step: 'contact' | 'preferences' | 'games' | 'uploadCV' | 'resultados'
  children: React.ReactNode
}

export default function ProtectedRoute({ step, children }: Props) {
  const personal = useSelector((state: any) => state.personal)
  const registered = Boolean(personal.firstName && personal.lastName)
  const completedGames = useSelector((state: any) => state.progress.completedGames || [])
  const cvUploaded = useSelector((state: any) => Boolean(state.progress.cvFile))
  const prefsCompleted = Boolean(personal.jobPreferences)

  switch (step) {
    case 'preferences':
      if (!registered) return <Navigate to="/register/contact" replace />
      return <>{children}</>

    case 'games':
      if (!registered) return <Navigate to="/register/contact" replace />
      return <>{children}</>

    case 'uploadCV':
      if (!registered) return <Navigate to="/register/contact" replace />
      if (completedGames.length < 10) return <Navigate to="/games" replace />
      return <>{children}</>

    case 'resultados':
      if (!registered) return <Navigate to="/register/contact" replace />
      if (completedGames.length < 10) return <Navigate to="/games" replace />
      if (!cvUploaded) return <Navigate to="/upload-cv" replace />
      if (!prefsCompleted) return <Navigate to="/preferences" replace />
      return <>{children}</>

    default:
      return <>{children}</>
  }
}