// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    // Entorno de prueba
    environment: 'jsdom',
    
    // Archivos de setup para mocks globales
    setupFiles: './src/setupTests.ts',
    
    // Rutas donde buscar tests
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    
    // Carpetas a ignorar
    exclude: [
      'node_modules',
      'dist',
      'public', 
      '.cache', 
      '.temp', 
      '*.log'
    ],
    
    // Configuración adicional útil
    globals: true,
    reporters: 'default',
    coverage: {
      provider: 'istanbul', // o 'v8' si prefieres
      reporter: ['text', 'json-summary', 'html'],
      reportsDirectory: './coverage'
    },
    deps: {
      inline: ['@testing-library/react']
    }
  }
})