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
    // Si hay una variable de entorno configurada, usarla
    if (import.meta.env.VITE_API_URL) {
      return import.meta.env.VITE_API_URL;
    }
    
    // Si estamos en Azure, usar el backend de Azure
    if (AZURE_CONFIG.isAzureEnvironment()) {
      return AZURE_CONFIG.AZURE_BACKEND_URL;
    }
    
    // Por defecto, usar localhost:8080 (pero el sistema puede detectar otros puertos)
    return AZURE_CONFIG.LOCAL_BACKEND_URLS[0];
  },
  
  // Función para detectar backend disponible (usada en desarrollo)
  detectAvailableBackend: async () => {
    for (const url of AZURE_CONFIG.LOCAL_BACKEND_URLS) {
      try {
        const response = await fetch(`${url}/health`, { 
          method: 'GET',
          signal: AbortSignal.timeout(2000) // 2 segundos timeout
        });
        if (response.ok) {
          console.log(`✅ Backend detectado en: ${url}`);
          return url;
        }
      } catch (error) {
        console.log(`❌ Backend no disponible en: ${url}`);
      }
    }
    console.log(`⚠️ No se detectó backend disponible, usando: ${AZURE_CONFIG.LOCAL_BACKEND_URLS[0]}`);
    return AZURE_CONFIG.LOCAL_BACKEND_URLS[0];
  }
}; 