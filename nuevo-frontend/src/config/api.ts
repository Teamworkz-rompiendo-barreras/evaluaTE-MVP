// Configuración centralizada de la API
export const API_CONFIG = {
  // En Vercel, frontend y backend están en el mismo dominio
  BASE_URL: '',

  // Endpoints específicos
  ENDPOINTS: {
    INFORME: '/api/informe-ia',
    IA_REPORT: '/api/analyze',           // Full employment report
    IA_FEEDBACK: '/api/informe-ia/feedback',
    PDF_GENERATE: '/api/report/generate',
    PDF_ANALYZE: '/api/pdf/analyze-cv',  // CV structure analysis (structure_score, contact, etc.)
    PDF_DOWNLOAD: '/api/report/generate',
    REPORT_LATEST: '/api/report/latest', // Load last saved report without regenerating
  }
};

// Función helper para construir URLs completas
export const buildApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

