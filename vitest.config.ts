// vitest.config.ts
import { defineConfig } from 'vitest/config'

// TypeScript ya no dará error al importar estos módulos
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    exclude: ['node_modules', 'dist']
  },
})