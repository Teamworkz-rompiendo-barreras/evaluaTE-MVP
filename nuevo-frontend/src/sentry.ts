/* eslint-disable no-console */
import * as Sentry from '@sentry/react';

// Configuración optimizada de Sentry
const sentryConfig = {
  enabled: import.meta.env['VITE_ENABLE_SENTRY_DEBUG'] === 'true' || import.meta.env.PROD,
  development: {
    tracesSampleRate: 0.1,
    replaysSessionSampleRate: 0.0,
    replaysOnErrorSampleRate: 0.1,
    debug: false,
  },
  production: {
    tracesSampleRate: 0.05,
    replaysSessionSampleRate: 0.01,
    replaysOnErrorSampleRate: 0.1,
    debug: false,
  },
};

// Inicializar Sentry
export function initSentry() {
  const dsn = import.meta.env['VITE_SENTRY_DSN'];
  
  // Solo inicializar si hay DSN y está habilitado
  if (!dsn || !sentryConfig.enabled) {
    console.log('🔍 Sentry deshabilitado - DSN no encontrado o no habilitado');
    return;
  }

  const config = import.meta.env.PROD ? sentryConfig.production : sentryConfig.development;

  try {
    Sentry.init({
      dsn,
      integrations: [
        Sentry.browserTracingIntegration(),
        Sentry.replayIntegration({
          maskAllText: false,
          blockAllMedia: false,
        }),
      ],
      tracesSampleRate: config.tracesSampleRate,
      replaysSessionSampleRate: config.replaysSessionSampleRate,
      replaysOnErrorSampleRate: config.replaysOnErrorSampleRate,
      
      beforeSend(event) {
        // Filtrar eventos duplicados y no deseados
        if (event.exception) {
          const exception = event.exception.values?.[0];
          if (exception?.type === 'ChunkLoadError') {
            return null;
          }
        }
        
        // Filtrar mensajes de redirección duplicados
        if (event.message && event.message.includes('Redirección de acceso')) {
          if (import.meta.env.PROD) {
            const now = Date.now();
            const lastRedirect = (window as any).__lastRedirectTime || 0;
            if (now - lastRedirect < 5000) {
              return null;
            }
            (window as any).__lastRedirectTime = now;
          }
        }
        
        return event;
      },
      
      environment: import.meta.env.MODE,
      release: import.meta.env['VITE_APP_VERSION'] || '1.0.0',
      debug: config.debug,
      
      initialScope: {
        tags: {
          app: 'evaluate',
          version: import.meta.env['VITE_APP_VERSION'] || '1.0.0',
        },
      },
    });
    
    console.log('✅ Sentry inicializado correctamente');
  } catch (error) {
    console.error('❌ Error al inicializar Sentry:', error);
  }
}

// Función para reportar errores manualmente
export function reportError(error: Error, context?: Record<string, unknown>) {
  const dsn = import.meta.env['VITE_SENTRY_DSN'];
  if (dsn && sentryConfig.enabled) {
    try {
      Sentry.captureException(error, {
        extra: context,
        tags: {
          source: 'manual_report',
        },
      });
    } catch (e) {
      console.error('Error al reportar a Sentry:', e);
    }
  }
}

// Función para reportar mensajes informativos con throttling
export function reportMessage(message: string, level: Sentry.SeverityLevel = 'info') {
  const dsn = import.meta.env['VITE_SENTRY_DSN'];
  if (dsn && sentryConfig.enabled) {
    try {
      // Throttling para mensajes de redirección
      if (message.includes('Redirección de acceso')) {
        const now = Date.now();
        const lastMessage = (window as any).__lastMessageTime || 0;
        if (now - lastMessage < 2000) {
          return;
        }
        (window as any).__lastMessageTime = now;
      }
      
      Sentry.captureMessage(message, level);
    } catch (e) {
      console.error('Error al reportar mensaje a Sentry:', e);
    }
  }
}

// Función para establecer contexto del usuario
export function setUserContext(user: { id: string; email?: string; name?: string }) {
  if (sentryConfig.enabled) {
    try {
      Sentry.setUser(user);
    } catch (e) {
      console.error('Error al establecer usuario en Sentry:', e);
    }
  }
}

// Función para limpiar contexto del usuario
export function clearUserContext() {
  if (sentryConfig.enabled) {
    try {
      Sentry.setUser(null);
    } catch (e) {
      console.error('Error al limpiar usuario en Sentry:', e);
    }
  }
} 