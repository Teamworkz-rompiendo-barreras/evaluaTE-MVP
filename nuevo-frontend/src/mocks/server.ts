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
 * 
 * Puedes usar esto desde `setupTests.ts` si estás usando Vitest o Jest
 */
server.listen({
  onUnhandledRequest: 'bypass' // Permite hacer llamadas reales no definidas aquí
})