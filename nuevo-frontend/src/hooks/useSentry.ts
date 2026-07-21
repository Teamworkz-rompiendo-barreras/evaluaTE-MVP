import { useCallback, useRef } from 'react';
import { reportError, reportMessage, setUserContext, clearUserContext } from '../sentry';

export const useSentry = () => {
  // Ref para evitar eventos duplicados
  const lastEventRef = useRef<{ message: string; timestamp: number } | null>(null);
  const throttleTime = 2000; // 2 segundos entre eventos similares

  // Función para reportar errores
  const captureError = useCallback((error: Error, context?: Record<string, unknown>) => {
    reportError(error, context);
  }, []);

  // Función para reportar mensajes con throttling inteligente
  const captureMessage = useCallback((message: string, level: 'info' | 'warning' | 'error' = 'info') => {
    const now = Date.now();
    const lastEvent = lastEventRef.current;
    
    // Evitar mensajes duplicados en un corto período
    if (lastEvent && 
        lastEvent.message === message && 
        now - lastEvent.timestamp < throttleTime) {
      return;
    }
    
    // Actualizar referencia del último evento
    lastEventRef.current = { message, timestamp: now };
    
    // Solo reportar mensajes importantes en desarrollo
    if (import.meta.env.DEV && level === 'info') {
      // En desarrollo, solo reportar warnings y errores
      if (message.includes('Redirección de acceso')) {
        return; // No reportar redirecciones en desarrollo
      }
    }
    
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
