import * as Sentry from '@sentry/react';

// Inicializar Sentry
export function initSentry() {
  // Solo inicializar en producción o cuando tengas un DSN real
  if (import.meta.env.PROD) {
    Sentry.init({
      dsn: import.meta.env.VITE_SENTRY_DSN || "https://tu-dsn-de-sentry@sentry.io/project-id",
      
      // Configuración de performance
      integrations: [
        Sentry.browserTracingIntegration(),
        Sentry.replayIntegration(),
      ],
      
      // Configuración de muestreo
      tracesSampleRate: 0.2, // 20% de las transacciones
      
      // Configuración de errores
      beforeSend(event) {
        // Filtrar errores que no queremos reportar
        if (event.exception) {
          const exception = event.exception.values?.[0];
          if (exception?.type === 'ChunkLoadError') {
            return null; // No reportar errores de carga de chunks
          }
        }
        return event;
      },
      
      // Configuración del entorno
      environment: import.meta.env.MODE,
      
      // Configuración de release
      release: import.meta.env.VITE_APP_VERSION || '1.0.0',
      
      // Configuración de debug (solo en desarrollo)
      debug: import.meta.env.DEV,
    });
  }
}

// Función para reportar errores manualmente
export function reportError(error: Error, context?: Record<string, any>) {
  if (import.meta.env.PROD) {
    Sentry.captureException(error, {
      extra: context,
    });
  } else {
    console.error('Error reportado a Sentry:', error, context);
  }
}

// Función para reportar mensajes informativos
export function reportMessage(message: string, level: Sentry.SeverityLevel = 'info') {
  if (import.meta.env.PROD) {
    Sentry.captureMessage(message, level);
  } else {
    console.log(`[Sentry ${level}]:`, message);
  }
}

// Función para agregar contexto del usuario
export function setUserContext(user: { id: string; email?: string; name?: string }) {
  if (import.meta.env.PROD) {
    Sentry.setUser(user);
  }
}

// Función para limpiar contexto del usuario
export function clearUserContext() {
  if (import.meta.env.PROD) {
    Sentry.setUser(null);
  }
} 