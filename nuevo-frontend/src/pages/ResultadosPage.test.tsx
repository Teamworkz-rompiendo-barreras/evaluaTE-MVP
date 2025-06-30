// src/pages/ResultadosPage.test.tsx
import { render } from '@testing-library/react'
import { screen } from '@testing-library/dom'
import '@testing-library/jest-dom'
import ResultadosPage from './ResultadosPage'

describe('ResultadosPage', () => {
  it('muestra el informe correctamente', () => {
    render(<ResultadosPage />)
    expect(screen.getByText('Tu Informe Final')).toBeInTheDocument()
  })
})