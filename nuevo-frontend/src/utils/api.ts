// src/utils/api.ts
import { API_CONFIG } from '../config/api';

export interface AccessibleErrorPayload {
  message: string;
  code: string;
  isAccessibleAlert: boolean;
}

export interface GenerateReportPayload {
  fullName?: string;
  cvAnalysis?: unknown;
  report?: unknown;
  [key: string]: unknown;
}

const verifyJsonContentType = (response: Response): void => {
  const contentType = response.headers.get('content-type');
  if (!contentType || !contentType.includes('application/json')) {
    throw new Error('SERVER_TIMEOUT_OR_INFRASTRUCTURE_FAILURE');
  }
};

// Restauramos la función que conecta con el endpoint de IA gamificada
export const sendProfileAnalysis = async (formData: FormData, userId: string): Promise<any> => {
  const controller = new AbortController();
  // 150 segundos para absorber latencia de LLM y backoffs del servidor
  const timeoutId = setTimeout(() => controller.abort(), 150000);

  const envBaseUrl = API_CONFIG.BASE_URL || 'http://localhost:8080';
  const baseUrl = envBaseUrl.replace(/\/$/, '');
  const url = `${baseUrl}${API_CONFIG.ENDPOINTS.IA_REPORT}`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      credentials: 'include',
      headers: {
        'X-User-Id': userId,
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    verifyJsonContentType(response);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      
      let finalMessage = errorData?.detail || 'Error interno en el procesamiento de tu informe.';
      
      // Mapeo defensivo de errores 422 (Pydantic de FastAPI)
      if (response.status === 422 && Array.isArray(errorData?.detail)) {
        const validationErrors = errorData.detail.map((err: any) => {
          const location = err.loc ? err.loc.join('.') : 'Campo desconocido';
          return `${location} (${err.msg})`;
        });
        finalMessage = `El servidor rechazó los datos (422): ${validationErrors.join(' | ')}`;
      } else if (typeof finalMessage === 'object') {
        finalMessage = JSON.stringify(finalMessage);
      }

      throw {
        message: finalMessage,
        code: 'ERR_SERVER_RESPONSE',
        isAccessibleAlert: true
      };
    }

    return await response.json();

  } catch (error: any) {
    clearTimeout(timeoutId);
    
    if (error.name === 'AbortError' || error.message === 'SERVER_TIMEOUT_OR_INFRASTRUCTURE_FAILURE') {
      throw {
        message: 'El servidor está tardando mucho en responder debido a alta demanda. Por favor, vuelve a intentarlo más tarde.',
        code: 'ERR_INFRASTRUCTURE_TIMEOUT',
        isAccessibleAlert: true
      };
    }
    
    throw {
      message: error.message || 'Error de conexión. Revisa tu acceso a internet o verifica que el puerto 8080 esté activo.',
      code: error.code || 'ERR_NETWORK',
      isAccessibleAlert: true
    };
  }
};