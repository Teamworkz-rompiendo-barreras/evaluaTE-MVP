import { useCallback } from 'react';
import { reportError, reportMessage, setUserContext, clearUserContext } from '../sentry';

export const useSentry = () => {
  // Función para reportar errores
  const captureError = useCallback((error: Error, context?: Record<string, unknown>) => {
    reportError(error, context);
  }, []);

  // Función para reportar mensajes
  const captureMessage = useCallback((message: string, level: 'info' | 'warning' | 'error' = 'info') => {
    reportMessage(message, level);
  }, []);

  // Función para establecer contexto del usuario
  const setUser = useCallback((user: { id: string; email?: string; name?: string }) => {
    setUserContext(user);
  }, []);

  // Función para limpiar contexto del usuario
  const clearUser = useCallback(() => {
    clearUserContext();
  }, []);

  // Función para agregar contexto adicional
  const addContext = useCallback((key: string, value: unknown) => {
    if (import.meta.env.PROD) {
      // En producción, usar Sentry.setContext
      import('@sentry/react').then(({ setContext }) => {
        setContext(key, value as Record<string, unknown>);
      });
    } else {
      // Aquí podrías agregar un log para desarrollo si lo necesitas
      // console.log('addContext:', key, value);
    }
  }, []);

  // Función para agregar tags
  const addTag = useCallback((key: string, value: string) => {
    if (import.meta.env.PROD) {
      import('@sentry/react').then(({ setTag }) => {
        setTag(key, value);
      });
    }
  }, []);

  return {
    captureError,
    captureMessage,
    setUser,
    clearUser,
    addContext,
    addTag,
  };
};