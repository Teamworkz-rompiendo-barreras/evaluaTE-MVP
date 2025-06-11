// src/setupTests.ts
import '@testing-library/jest-dom'            // 1) importa los estilos y matchers
import matchers from '@testing-library/jest-dom/matchers'
import { expect } from 'vitest'

// 2) registra los matchers de jest-dom en Vitest
expect.extend(matchers)
