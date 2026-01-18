import { AZURE_CONFIG } from './azure-config';

// Configuración centralizada de la API
export const API_CONFIG = {
  // Usar la detección automática de Azure
  BASE_URL: 'https://evaluate-backend.onrender.com',

  // Endpoints específicos
  ENDPOINTS: {
    INFORME: '/api/informe-ia',
    // Mantener compatibilidad con endpoints existentes si es necesario
    IA_REPORT: '/api/informe-ia',
    IA_FEEDBACK: '/api/informe-ia/feedback',
    PDF_GENERATE: '/api/pdf/generate-report',
    PDF_ANALYZE: '/api/pdf/analyze-cv',
    PDF_DOWNLOAD: '/api/pdf/generate-report'
  }
};

// Función helper para construir URLs completas
export const buildApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};
