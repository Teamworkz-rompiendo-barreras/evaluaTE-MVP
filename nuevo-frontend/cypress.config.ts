// cypress.config.ts
import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    // Dirección donde corre tu frontend
    baseUrl: 'http://localhost:5173',

    // Rutas de tus tests end-to-end
    specPattern: 'cypress/e2e/**/*.cy.{js,ts,jsx,tsx}',

    // Configuración adicional para Cypress UI
    supportFile: 'cypress/support/index.ts',
    viewportWidth: 1440,
    viewportHeight: 900,

    // Integración con backend (opcional)
    env: {
      API_URL: '/api',
      SCENE_PATH: '/api/scenes',
      LOGS_PATH: '/api/logs',
    },

    // Para evitar timeouts innecesarios
    defaultCommandTimeout: 10000,
    execTimeout: 60000,
    taskTimeout: 60000,

    // Si usas variables de entorno personalizadas
    setupNodeEvents(on, config) {
      // Ejemplo: puedes añadir plugins o logs aquí
      on('task', {
        log(message) {
          console.log(message)
          return null
        },
      })

      return config
    },
  },
})