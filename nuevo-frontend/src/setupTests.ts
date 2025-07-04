/// <reference types="vitest/globals" />

import '@testing-library/jest-dom'
import '@testing-library/jest-dom/extend-expect'
import { server } from './mocks/server'

// Inicia el servidor mock antes de todas las pruebas
beforeAll(() => {
  server.listen()
})

// Reinicia los handlers después de cada prueba
afterEach(() => {
  server.resetHandlers()
})

// Detiene el servidor al finalizar
afterAll(() => {
  server.close()
})