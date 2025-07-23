// Configuración específica para Azure
export const AZURE_CONFIG = {
  // Detectar si estamos en Azure Static Web Apps
  isAzureEnvironment: () => {
    return window.location.hostname.includes('azurestaticapps.net') ||
           window.location.hostname.includes('azurewebsites.net') ||
           import.meta.env.PROD;
  },
  
  // URL del backend en Azure
  AZURE_BACKEND_URL: 'https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net',
  
  // URL local para desarrollo
  LOCAL_BACKEND_URL: 'http://localhost:8080',
  
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
    
    // Por defecto, usar localhost
    return AZURE_CONFIG.LOCAL_BACKEND_URL;
  }
}; 