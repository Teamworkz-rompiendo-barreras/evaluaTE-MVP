// Configuración de Sentry para desarrollo
export const sentryConfig = {
  // En desarrollo, desactivar Sentry por defecto
  enabled: import.meta.env['VITE_ENABLE_SENTRY_DEBUG'] === 'true',
  
  // Configuración de desarrollo
  development: {
    tracesSampleRate: 0.1, // Solo 10% de las transacciones
    replaysSessionSampleRate: 0.0, // No grabar sesiones en desarrollo
    replaysOnErrorSampleRate: 0.1, // Solo grabar errores
    debug: false,
  },
  
  // Configuración de producción
  production: {
    tracesSampleRate: 0.05, // Solo 5% de las transacciones
    replaysSessionSampleRate: 0.01, // Solo 1% de las sesiones
    replaysOnErrorSampleRate: 0.1, // Solo 10% de los errores
    debug: false,
  },
};
