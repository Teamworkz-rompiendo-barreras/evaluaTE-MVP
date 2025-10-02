// Configuración específica para Azure
export const AZURE_CONFIG = {
  // Detectar si estamos en Azure Static Web Apps
  isAzureEnvironment: () => {
    return window.location.hostname.includes('azurestaticapps.net') ||
           window.location.hostname.includes('azurewebsites.net') ||
           import.meta.env.PROD;
  },
  
  // URL del backend en Azure (sin puerto, Azure maneja el enrutamiento)
  AZURE_BACKEND_URL: 'https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net',
  
  // URLs locales para desarrollo (múltiples puertos comunes)
  LOCAL_BACKEND_URLS: [
    'http://localhost:8080',
    'http://localhost:8181',
    'http://localhost:8000',
    'http://localhost:3001'
  ],
  
  // Obtener la URL correcta del backend
  getBackendUrl: () => {
    if (import.meta.env.MODE !== 'production') {
      // eslint-disable-next-line no-console
      console.log('🔍 DEBUG - Detectando URL del backend...');
      // eslint-disable-next-line no-console
      console.log('🔍 DEBUG - window.location.hostname:', window.location.hostname);
      // eslint-disable-next-line no-console
      console.log('🔍 DEBUG - import.meta.env.PROD:', import.meta.env.PROD);
      // eslint-disable-next-line no-console
      console.log('🔍 DEBUG - import.meta.env.VITE_API_URL:', import.meta.env['VITE_API_URL']);
    }
    
    // Si hay una variable de entorno configurada, usarla
    if (import.meta.env['VITE_API_URL']) {
      // Evitar log en producción
      return import.meta.env['VITE_API_URL'];
    }
    
    // Si estamos en Azure, usar el backend de Azure
    const isAzure = AZURE_CONFIG.isAzureEnvironment();
    if (isAzure) {
      if (import.meta.env.MODE !== 'production') {
        // eslint-disable-next-line no-console
        console.log('✅ DEBUG - Entorno Azure detectado. Backend:', AZURE_CONFIG.AZURE_BACKEND_URL);
      }
      return AZURE_CONFIG.AZURE_BACKEND_URL;
    }

    // Desarrollo/local: usar PROXY de Vite (mismo origen) para evitar CORS
    const host = (typeof window !== 'undefined' ? window.location.hostname : '') || '';
    const isLocalHost = host === 'localhost' || host === '127.0.0.1' || host === '::1';
    if (isLocalHost || import.meta.env.MODE !== 'production') {
      if (import.meta.env.MODE !== 'production') {
        // eslint-disable-next-line no-console
        console.log('✅ DEBUG - Entorno local: usando "same-origin" (ruta /api → proxy Vite)');
      }
      // Construir URLs relativas: /api/...
      return '';
    }

    // Fallback seguro: Azure público
    if (import.meta.env.MODE !== 'production') {
      // eslint-disable-next-line no-console
      console.log('⚠️ DEBUG - Fallback a Azure backend (no local detectado)');
    }
    return AZURE_CONFIG.AZURE_BACKEND_URL;
  },
  
  // Función para detectar backend disponible (usada en desarrollo)
  detectAvailableBackend: async () => {
    for (const url of AZURE_CONFIG.LOCAL_BACKEND_URLS) {
      try {
        const response = await fetch(`${url}/health`, { 
          method: 'GET',
          signal: AbortSignal.timeout(5000) // Aumenta timeout de detección a 5s
        });
        if (response.ok) {
          if (import.meta.env.MODE !== 'production') {
            // eslint-disable-next-line no-console
            console.log(`✅ Backend detectado en: ${url}`);
          }
          return url;
        }
      } catch (error) {
        if (import.meta.env.MODE !== 'production') {
          // eslint-disable-next-line no-console
          console.log(`❌ Backend no disponible en: ${url}`);
        }
      }
    }
    if (import.meta.env.MODE !== 'production') {
      // eslint-disable-next-line no-console
      console.log(`⚠️ No se detectó backend disponible, usando: ${AZURE_CONFIG.LOCAL_BACKEND_URLS[0]}`);
    }
    return AZURE_CONFIG.LOCAL_BACKEND_URLS[0];
  }
}; 