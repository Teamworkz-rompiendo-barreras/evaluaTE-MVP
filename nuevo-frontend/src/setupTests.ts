/// <reference types="vitest/globals" />

import '@testing-library/jest-dom'
import { beforeEach, vi } from 'vitest'

// Configuración básica para tests
beforeEach(() => {
  // Limpiar cualquier estado residual
  vi.clearAllMocks()
})