/// <reference types="vitest/globals" />

import '@testing-library/jest-dom'

// Configuración básica para tests
beforeEach(() => {
  // Limpiar cualquier estado residual
  vi.clearAllMocks()
})