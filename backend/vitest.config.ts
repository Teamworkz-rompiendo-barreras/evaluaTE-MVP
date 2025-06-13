// backend/vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    // Incluye cualquier .test.ts en el proyecto
    include: ['**/*.test.ts'],
    exclude: ['node_modules', 'dist', 'cypress']
  }
})
