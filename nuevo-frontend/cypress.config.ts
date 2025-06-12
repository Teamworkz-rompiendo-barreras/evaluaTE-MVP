// nuevo-frontend/cypress.config.ts
import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    // carpeta donde están tus specs
    specPattern: 'cypress/e2e/**/*.cy.{js,ts,jsx,tsx}',
    // aquí apuntas al servidor de desarrollo
    baseUrl: 'http://localhost:5173',
    supportFile: false, // o 'cypress/support/index.ts' si tienes custom commands
  },
})
