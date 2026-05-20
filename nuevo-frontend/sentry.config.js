/* eslint-disable no-undef */
// Configuración de Sentry para el proyecto EvaluaTE
// Para obtener tu DSN: https://sentry.io/settings/projects/[tu-proyecto]/keys/

module.exports = {
  // Configuración del proyecto
  project: 'evaluate-frontend',
  org: 'tu-organizacion',
  
  // Configuración de releases
  release: process.env.VITE_APP_VERSION || '1.0.0',
  
  // Configuración de entornos
  environment: process.env.NODE_ENV || 'development',
  
  // Configuración de muestreo
  tracesSampleRate: 0.2,
  
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
  
  // Configuración de contexto
  defaultTags: {
    app: 'evaluate',
    version: process.env.VITE_APP_VERSION || '1.0.0',
  },
}; 