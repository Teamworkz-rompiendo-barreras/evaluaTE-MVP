// src/components/ProtectedRoute.tsx
import React, { useMemo } from 'react';
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

  // Memoizar las verificaciones para evitar recálculos innecesarios
  const routeChecks = useMemo(() => {
    const hasContactData = Boolean(personal.firstName && personal.lastName);
    const hasPreferences = Boolean(
      personal.jobPreferences &&
      (
        typeof personal.jobPreferences === 'string'
          ? personal.jobPreferences.trim() !== ''
          : Array.isArray(personal.jobPreferences?.areas)
            ? personal.jobPreferences?.areas?.length > 0 && personal.jobPreferences?.areas?.[0]?.trim() !== ''
            : false
      )
    );
    const hasPersonalData = personal.completed;
    const hasCompletedAllGames = game.completedGames && game.completedGames.length >= 10;
    const hasCV = Boolean(personal.cvFile && personal.cvFile.fileName);

    return {
      hasContactData,
      hasPreferences,
      hasPersonalData,
      hasCompletedAllGames,
      hasCV,
      completedGames: game.completedGames.length,
    };
  }, [personal, game]);

  // Agregar contexto a Sentry solo cuando sea necesario
  React.useEffect(() => {
    if (import.meta.env.PROD) {
      addContext('protectedRoute', {
        step,
        pathname: location.pathname,
        ...routeChecks,
      });
    }
  }, [step, location.pathname, routeChecks, addContext]);

  // Función de redirección optimizada
  const redirectTo = React.useCallback((path: string) => {
    // Solo reportar redirecciones importantes en producción
    if (import.meta.env.PROD) {
      captureMessage(`Redirección de acceso: ${step} → ${path}`, 'info');
    }
    return <Navigate to={path} replace state={{ from: location }} />;
  }, [step, location, captureMessage]);

  // Lógica de protección por paso
  switch (step) {
    case 'contact':
      return <>{children}</>;

    case 'preferences':
      if (!routeChecks.hasContactData) {
        return redirectTo('/register/contact');
      }
      return <>{children}</>;

    case 'games':
      if (!routeChecks.hasPersonalData) {
        return redirectTo('/register/contact');
      }
      return <>{children}</>;

    case 'uploadCV':
      if (!routeChecks.hasPersonalData) {
        return redirectTo('/register/contact');
      }
      if (!routeChecks.hasCompletedAllGames) {
        return redirectTo('/games');
      }
      if (routeChecks.hasCV) {
        return redirectTo('/resultados');
      }
      return <>{children}</>;

    case 'resultados':
      if (!routeChecks.hasPersonalData) {
        return redirectTo('/register/contact');
      }
      if (!routeChecks.hasCompletedAllGames) {
        return redirectTo('/games');
      }
      if (!routeChecks.hasCV) {
        return redirectTo('/upload-cv');
      }
      return <>{children}</>;

    default:
      return redirectTo('/register/contact');
  }
}