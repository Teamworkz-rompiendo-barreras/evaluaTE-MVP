// src/components/ProtectedRoute.tsx
import React from 'react'
import { useSelector } from 'react-redux'
import { Navigate, useNavigate } from 'react-router-dom'

import type { RootState } from '@/app/store'
import type { PersonalState } from '@/features/personal/personalSlice'

interface Props {
  step: 'contact' | 'preferences' | 'games' | 'uploadCV' | 'resultados'
  children: React.ReactNode
}

export default function ProtectedRoute({ step, children }: Props) {
  const navigate = useNavigate()
  const personal = useSelector((state: RootState) => state.personal)
  const progress = useSelector((state: RootState) => state.progress)

  const hasPersonalData = Boolean(personal.firstName && personal.lastName)
  const hasCV = Boolean(personal.cvFile)
  const hasPreferences = Boolean(personal.jobPreferences)
  const hasCompletedAllGames = progress.completedGames.length >= 10

  // Redirección genérica – para evitar repetir código
  const redirectToStep = (target: string) => {
    return <Navigate to={target} replace />
  }

  switch (step) {
    case 'contact':
      if (!hasPersonalData) return <>{children}</>
      // Si ya tiene datos personales, redirigimos al siguiente paso
      return redirectToStep('/preferences')

    case 'preferences':
      if (!hasPersonalData) return redirectToStep('/register/contact')
      if (hasPreferences) return <>{children}</>
      // Si no hay preferencias, deja continuar
      return <>{children}</>

    case 'games':
      if (!hasPersonalData) return redirectToStep('/register/contact')
      return <>{children}</>

    case 'uploadCV':
      if (!hasPersonalData) return redirectToStep('/register/contact')
      if (!hasCompletedAllGames) return redirectToStep('/games')
      return <>{children}</>

    case 'resultados':
      if (!hasPersonalData) return redirectToStep('/register/contact')
      if (!hasCompletedAllGames) return redirectToStep('/games')
      if (!hasCV) return redirectToStep('/upload-cv')
      if (!hasPreferences) return redirectToStep('/preferences')
      return <>{children}</>

    default:
      return <>{children}</>
  }
}