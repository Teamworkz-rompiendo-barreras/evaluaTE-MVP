import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'jsdom',        // simulación de navegador
    globals: true,               // permite usar expect() sin importarlo
    setupFiles: './src/setupTests.ts' // fichero para cargar jest-dom
  }
})
