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

  // Verificar si los datos de contacto están completos
  const hasContactData = Boolean(personal.firstName && personal.lastName);
  
  // Verificar si las preferencias están completas
  const hasPreferences = personal?.jobPreferences && (
    typeof personal.jobPreferences === 'string' 
      ? personal.jobPreferences.trim() !== ''
      : personal.jobPreferences.areas && personal.jobPreferences.areas.length > 0
  );
  
  console.log('ProtectedRoute - jobPreferences type:', typeof personal?.jobPreferences);
  console.log('ProtectedRoute - jobPreferences value:', personal?.jobPreferences);
  if (typeof personal?.jobPreferences === 'object') {
    console.log('ProtectedRoute - jobPreferences.areas:', personal?.jobPreferences?.areas);
  }
  
  // Los datos personales están completamente completos cuando se tienen tanto contact como preferences
  const hasPersonalData = hasContactData && hasPreferences;
  
  const hasCV = Boolean(personal.cvFile && personal.cvFile.fileName);
  // Usar el slice de game para los juegos completados
  const hasCompletedAllGames = game.completedGames.length >= 10;

  console.log('ProtectedRoute - step:', step);
  console.log('ProtectedRoute - personal:', personal);
  console.log('ProtectedRoute - hasContactData:', hasContactData);
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
      if (!hasContactData) return redirectToStep('/register/contact');
      if (!hasPreferences) return <>{children}</>;
      // Si ya tiene preferencias, redirigimos al siguiente paso
      return redirectToStep('/games');

    case 'games':
      if (!hasContactData) return redirectToStep('/register/contact');
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