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
  const game = useSelector((state: RootState) => state.game);

  console.log('🔒 ProtectedRoute - INICIO');
  console.log('🔒 ProtectedRoute - step:', step);
  console.log('🔒 ProtectedRoute - location.pathname:', location.pathname);
  console.log('🔒 ProtectedRoute - personal:', personal);
  console.log('🔒 ProtectedRoute - personal.completed:', personal.completed);

  // Verificaciones simplificadas
  const hasContactData = Boolean(personal.firstName && personal.lastName);
  const hasPreferences = Boolean(
    personal.jobPreferences && 
    (typeof personal.jobPreferences === 'string' 
      ? personal.jobPreferences.trim() !== ''
      : personal.jobPreferences.areas && personal.jobPreferences.areas.length > 0)
  );
  const hasPersonalData = hasContactData && (hasPreferences || personal.completed);
  const hasCompletedAllGames = game.completedGames.length >= 10;
  const hasCV = Boolean(personal.cvFile && personal.cvFile.fileName);

  console.log('🔒 ProtectedRoute - hasContactData:', hasContactData);
  console.log('🔒 ProtectedRoute - hasPreferences:', hasPreferences);
  console.log('🔒 ProtectedRoute - hasPersonalData:', hasPersonalData);
  console.log('🔒 ProtectedRoute - hasCompletedAllGames:', hasCompletedAllGames);
  console.log('🔒 ProtectedRoute - hasCV:', hasCV);

  // Función de redirección
  const redirectTo = (path: string) => {
    console.log('🔒 ProtectedRoute - REDIRIGIENDO a:', path);
    return <Navigate to={path} replace state={{ from: location }} />;
  };

  // Lógica de protección por paso
  switch (step) {
    case 'contact':
      // Siempre permitir acceso a contact
      console.log('🔒 ProtectedRoute - PERMITIENDO acceso a contact');
      return <>{children}</>;

    case 'preferences':
      // Requiere datos de contacto
      if (!hasContactData) {
        console.log('🔒 ProtectedRoute - BLOQUEANDO preferences: no hay contact data');
        return redirectTo('/register/contact');
      }
      console.log('🔒 ProtectedRoute - PERMITIENDO acceso a preferences');
      return <>{children}</>;

    case 'games':
      // Requiere datos personales completos
      if (!hasContactData) {
        console.log('🔒 ProtectedRoute - BLOQUEANDO games: no hay contact data');
        return redirectTo('/register/contact');
      }
      if (!hasPersonalData) {
        console.log('🔒 ProtectedRoute - BLOQUEANDO games: no hay personal data completo');
        return redirectTo('/register/preferences');
      }
      console.log('🔒 ProtectedRoute - PERMITIENDO acceso a games');
      return <>{children}</>;

    case 'uploadCV':
      // Requiere datos personales y juegos completados
      if (!hasPersonalData) {
        console.log('🔒 ProtectedRoute - BLOQUEANDO uploadCV: no hay personal data');
        return redirectTo('/register/contact');
      }
      if (!hasCompletedAllGames) {
        console.log('🔒 ProtectedRoute - BLOQUEANDO uploadCV: no hay juegos completados');
        return redirectTo('/games');
      }
      if (hasCV) {
        console.log('🔒 ProtectedRoute - REDIRIGIENDO uploadCV: ya tiene CV');
        return redirectTo('/resultados');
      }
      console.log('🔒 ProtectedRoute - PERMITIENDO acceso a uploadCV');
      return <>{children}</>;

    case 'resultados':
      // Requiere todo completo
      if (!hasPersonalData) {
        console.log('🔒 ProtectedRoute - BLOQUEANDO resultados: no hay personal data');
        return redirectTo('/register/contact');
      }
      if (!hasCompletedAllGames) {
        console.log('🔒 ProtectedRoute - BLOQUEANDO resultados: no hay juegos completados');
        return redirectTo('/games');
      }
      if (!hasCV) {
        console.log('🔒 ProtectedRoute - BLOQUEANDO resultados: no hay CV');
        return redirectTo('/upload-cv');
      }
      console.log('🔒 ProtectedRoute - PERMITIENDO acceso a resultados');
      return <>{children}</>;

    default:
      console.log('🔒 ProtectedRoute - PASO DESCONOCIDO, redirigiendo a contact');
      return redirectTo('/register/contact');
  }
}