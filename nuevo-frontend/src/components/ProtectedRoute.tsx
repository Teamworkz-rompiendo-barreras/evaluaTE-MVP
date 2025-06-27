// src/components/ProtectedRoute.tsx
import React from 'react'
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'

interface Props {
  step: 'contact' | 'games' | 'uploadCV' | 'preferences' | 'resultados'
  children: React.ReactNode
}

export default function ProtectedRoute({ step, children }: Props) {
  const personal = useSelector((state: any) => state.personal)
  const registered      = Boolean(personal.firstName && personal.lastName)
  const completedGames  = useSelector((state: any) => state.progress.completedGames || [])   // array de ids
  const cvUploaded      = useSelector((state: any) => Boolean(state.progress.cvFile))       // true si hay CV
  const prefsCompleted  = Boolean(personal.jobPreferences)

  // Redirecciones según paso
  switch (step) {
    case 'games':
      if (!registered)       return <Navigate to="/register/contact" replace />
      return <>{children}</>

    case 'uploadCV':
      if (!registered)       return <Navigate to="/register/contact" replace />
      if (completedGames.length < 10) return <Navigate to="/games" replace />
      return <>{children}</>

    case 'preferences':
      if (!registered)       return <Navigate to="/register/contact" replace />
      if (completedGames.length < 10) return <Navigate to="/games" replace />
      if (!cvUploaded)       return <Navigate to="/upload-cv" replace />
      return <>{children}</>

    case 'resultados':
      if (!registered)       return <Navigate to="/register/contact" replace />
      if (completedGames.length < 10) return <Navigate to="/games" replace />
      if (!cvUploaded)       return <Navigate to="/upload-cv" replace />
      if (!prefsCompleted)   return <Navigate to="/preferences" replace />
      return <>{children}</>

    default:
      return <>{children}</>
  }
}
