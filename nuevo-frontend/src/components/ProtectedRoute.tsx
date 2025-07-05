// src/components/ProtectedRoute.tsx
import React from 'react';
import { useSelector } from 'react-redux';
import { Navigate, useLocation } from 'react-router-dom';

import type { RootState } from '@/app/store';

interface Props {
  step: 'contact' | 'preferences' | 'games' | 'uploadCV' | 'resultados';
  children: React.ReactNode;
}

export default function ProtectedRoute({ step, children }: Props) {
  const location = useLocation();
  const personal = useSelector((state: RootState) => state.personal);
  const progress = useSelector((state: RootState) => state.progress);
  const game = useSelector((state: RootState) => state.game);

  // Usar el nuevo campo completed para verificar si los datos personales están completos
  const hasPersonalData = personal.completed;
  const hasCV = Boolean(personal.cvFile && personal.cvFile.fileName);
  const hasPreferences = personal?.jobPreferences && (
    typeof personal.jobPreferences === 'string' 
      ? personal.jobPreferences.trim() !== ''
      : personal.jobPreferences.areas && personal.jobPreferences.areas.length > 0
  );
  // Usar el slice de game para los juegos completados
  const hasCompletedAllGames = game.completedGames.length >= 10;

  console.log('ProtectedRoute - step:', step);
  console.log('ProtectedRoute - personal:', personal);
  console.log('ProtectedRoute - hasPersonalData (completed):', hasPersonalData);
  console.log('ProtectedRoute - hasPreferences:', hasPreferences);
  console.log('ProtectedRoute - hasCV:', hasCV);
  console.log('ProtectedRoute - hasCompletedAllGames:', hasCompletedAllGames);
  console.log('ProtectedRoute - progress:', progress);
  console.log('ProtectedRoute - game:', game);

  // Redirección genérica – para evitar repetir código
  const redirectToStep = (target: string) => {
    return <Navigate to={target} replace state={{ from: location }} />;
  };

  switch (step) {
    case 'contact':
      return redirectToStep('/register/contact');

    case 'preferences':
      if (!hasPersonalData) return redirectToStep('/register/contact');
      if (!hasPreferences) return <>{children}</>;
      // Si ya tiene preferencias, redirigimos al siguiente paso
      return redirectToStep('/games');

    case 'games':
      if (!hasPersonalData) return redirectToStep('/register/contact');
      if (!hasPreferences) return redirectToStep('/register/preferences');
      return <>{children}</>;

    case 'uploadCV':
      if (!hasPersonalData) return redirectToStep('/register/contact');
      if (!hasCompletedAllGames) return redirectToStep('/games');
      if (hasCV) return redirectToStep('/resultados');
      return <>{children}</>;

    case 'resultados':
      if (!hasPersonalData) return redirectToStep('/register/contact');
      if (!hasCompletedAllGames) return redirectToStep('/games');
      if (!hasCV) return redirectToStep('/upload-cv');
      if (!hasPreferences) return redirectToStep('/register/preferences');
      return <>{children}</>;

    default:
      return redirectToStep('/register/contact');
  }
}