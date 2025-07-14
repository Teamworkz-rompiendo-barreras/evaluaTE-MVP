// src/components/ProtectedRoute.tsx
import React from 'react';
import { useSelector } from 'react-redux';
import { Navigate, useLocation } from 'react-router-dom';
import type { RootState } from '@/app/store';
import { useSentry } from '../hooks/useSentry';

interface Props {
  step: 'contact' | 'preferences' | 'games' | 'uploadCV' | 'resultados';
  children: React.ReactNode;
}

export default function ProtectedRoute({ step, children }: Props) {
  const location = useLocation();
  const personal = useSelector((state: RootState) => state.personal);
  const game = useSelector((state: RootState) => state.game);
  const { captureMessage, addContext } = useSentry();

  // Verificaciones robustas y tolerantes a formatos
  const hasContactData = Boolean(personal.firstName && personal.lastName);
  const hasPreferences = Boolean(
    personal.jobPreferences &&
    (
      typeof personal.jobPreferences === 'string'
        ? personal.jobPreferences.trim() !== ''
        : Array.isArray(personal.jobPreferences.areas)
          ? personal.jobPreferences.areas.length > 0 && personal.jobPreferences.areas[0].trim() !== ''
          : false
    )
  );
  // Usar el flag completed para la protección
  const hasPersonalData = personal.completed;
  const hasCompletedAllGames = game.completedGames && game.completedGames.length >= 10;
  const hasCV = Boolean(personal.cvFile && personal.cvFile.fileName);

  // Agregar contexto a Sentry
  addContext('protectedRoute', {
    step,
    pathname: location.pathname,
    hasContactData,
    hasPreferences,
    hasPersonalData,
    hasCompletedAllGames,
    hasCV,
    completedGames: game.completedGames.length,
  });

  // (console.log eliminado para evitar advertencias de lint)

  // Función de redirección
  const redirectTo = (path: string) => {
    captureMessage(`Redirección de acceso: ${step} → ${path}`, 'info');
    return <Navigate to={path} replace state={{ from: location }} />;
  };

  // Lógica de protección por paso
  switch (step) {
    case 'contact':
      // Siempre permitir acceso a contact
      return <>{children}</>;

    case 'preferences':
      // Solo redirigir si realmente faltan datos de contacto
      if (!hasContactData) {
        return redirectTo('/register/contact');
      }
      return <>{children}</>;

    case 'games':
      if (!hasPersonalData) {
        return redirectTo('/register/contact');
      }
      return <>{children}</>;

    case 'uploadCV':
      // Solo redirigir si realmente faltan datos personales completos o juegos
      if (!hasPersonalData) {
        return redirectTo('/register/contact');
      }
      if (!hasCompletedAllGames) {
        return redirectTo('/games');
      }
      if (hasCV) {
        return redirectTo('/resultados');
      }
      return <>{children}</>;

    case 'resultados':
      // Solo redirigir si realmente falta algo
      if (!hasPersonalData) {
        return redirectTo('/register/contact');
      }
      if (!hasCompletedAllGames) {
        return redirectTo('/games');
      }
      if (!hasCV) {
        return redirectTo('/upload-cv');
      }
      return <>{children}</>;

    default:
      return redirectTo('/register/contact');
  }
}