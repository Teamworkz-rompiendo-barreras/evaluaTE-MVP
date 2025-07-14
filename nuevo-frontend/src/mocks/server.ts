/* eslint-disable no-undef */
// src/mocks/server.ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

/**
 * Configura un servidor mock para interceptar llamadas HTTP durante el desarrollo
 * y las pruebas. Esto permite simular respuestas del backend sin conexión real.
 */
export const server = setupServer(...handlers)

/**
 * Inicia el servidor de mocks antes de cada prueba o ejecución local
 */
server.listen({
  onUnhandledRequest: 'bypass' // Permite hacer llamadas reales no definidas aquí
})

// Opcional: log de inicio (útil para debug)
if (import.meta.env.mode === 'test') {
  // console.log('[MSW] Mock server is running in test mode.')
} else if (process.env.NODE_ENV === 'development') {
  // console.log('[MSW] Mock server is running in development mode.')
}