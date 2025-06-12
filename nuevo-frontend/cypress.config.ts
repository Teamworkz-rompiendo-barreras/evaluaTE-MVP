import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',   // ➜ aquí apuntas a tu servidor Vite
    specPattern: 'cypress/e2e/**/*.cy.{js,ts,jsx,tsx}',
    setupNodeEvents (on, config) {
      // si tienes algo que hacer en events...
      return config
    },
  },
})
