import * as Sentry from '@sentry/react';

// Inicializar Sentry
export function initSentry() {
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  if (dsn) {
    Sentry.init({
      dsn,
      integrations: [
        Sentry.browserTracingIntegration(),
        Sentry.replayIntegration(),
      ],
      tracesSampleRate: 0.2,
      beforeSend(event) {
        if (event.exception) {
          const exception = event.exception.values?.[0];
          if (exception?.type === 'ChunkLoadError') {
            return null;
          }
        }
        return event;
      },
      environment: import.meta.env.MODE,
      release: import.meta.env.VITE_APP_VERSION || '1.0.0',
      debug: import.meta.env.DEV,
    });
  }
}

// Función para reportar errores manualmente
export function reportError(error: Error, context?: Record<string, any>) {
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  if (dsn) {
    Sentry.captureException(error, {
      extra: context,
    });
  } else {
    console.error('Error reportado a Sentry:', error, context);
  }
}

// Función para reportar mensajes informativos
export function reportMessage(message: string, level: Sentry.SeverityLevel = 'info') {
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  if (dsn) {
    Sentry.captureMessage(message, level);
  } else {
    console.log(`[Sentry ${level}]:`, message);
  }
}

// Función para agregar contexto del usuario
export function setUserContext(user: { id: string; email?: string; name?: string }) {
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  if (dsn) {
    Sentry.setUser(user);
  }
}

// Función para limpiar contexto del usuario
export function clearUserContext() {
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  if (dsn) {
    Sentry.setUser(null);
  }
} 