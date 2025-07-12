import { AZURE_CONFIG } from './azure-config';

// Configuración centralizada de la API
export const API_CONFIG = {
  // Usar la detección automática de Azure
  BASE_URL: AZURE_CONFIG.getBackendUrl(),
  
  // Endpoints específicos
  ENDPOINTS: {
    IA_REPORT: '/api/informe-ia',
    IA_FEEDBACK: '/api/informe-ia/feedback',
    PDF_GENERATE: '/api/generate-report',
    PDF_UPLOAD: '/api/upload-cv'
  }
};

// Función helper para construir URLs completas
export const buildApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
}; 