import { API_CONFIG } from '../config/api';

// Tipos mínimos para evitar any
export interface GenerateReportPayload {
  fullName?: string;
  cvAnalysis?: unknown;
  report?: unknown;
  [key: string]: unknown;
}

// Función para generar el informe completo
export async function generarInforme(payload: GenerateReportPayload, cvFile?: File) {
  const fd = new FormData();
  fd.append("payload", JSON.stringify(payload));
  if (cvFile) fd.append("cv", cvFile); // opcional

  const res = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.INFORME}`, {
    method: "POST",
    body: fd,
  });
  if (!res.ok) throw new Error(`Error ${res.status}`);
  return res.json();
}

// Función para obtener el informe existente (si es necesario)
export async function obtenerInforme(userId: string) {
  const res = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.INFORME}?userId=${userId}`, {
    method: "GET",
  });
  if (!res.ok) throw new Error(`Error ${res.status}`);
  return res.json();
}
