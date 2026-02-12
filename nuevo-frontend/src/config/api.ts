// Configuración centralizada de la API
export const API_CONFIG = {
  // En Vercel, frontend y backend están en el mismo dominio
  BASE_URL: '',

  // Endpoints específicos
  ENDPOINTS: {
    INFORME: '/api/informe-ia',
    // Mantener compatibilidad con endpoints existentes si es necesario
    IA_REPORT: '/api/analyze', // Updated to new endpoint
    IA_FEEDBACK: '/api/informe-ia/feedback',
    PDF_GENERATE: '/api/report/generate', // Updated to new endpoint
    PDF_ANALYZE: '/api/analyze', // Updated to match backend
    PDF_DOWNLOAD: '/api/report/generate' // Updated to new endpoint
  }
};

// Función helper para construir URLs completas
export const buildApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

