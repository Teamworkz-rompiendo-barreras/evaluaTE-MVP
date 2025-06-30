// src/pages/ResultadosPage.test.tsx

import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import ResultadosPage from './ResultadosPage'

describe('ResultadosPage', () => {
  it('muestra el informe correctamente', () => {
    render(<ResultadosPage />)
    expect(screen.getByText('Tu Informe Final')).toBeInTheDocument()
  })
})