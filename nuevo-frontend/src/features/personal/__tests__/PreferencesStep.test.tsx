/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import { store } from '../../../app/store'
import PreferencesStep from '../PreferencesStep'

describe('PreferencesStep', () => {
  function setup() {
    render(
      <Provider store={store}>
        <BrowserRouter>
          <PreferencesStep />
        </BrowserRouter>
      </Provider>
    )
  }

  it('muestra los campos y el botón de Finalizar', () => {
    setup()
    // Buscamos el input por su label y comprobamos que existe
    const jobInput = screen.getByLabelText(/tipo de trabajo/i)
    expect(jobInput).toBeDefined()

    // Buscamos todos los botones "Finalizar" y comprobamos que hay al menos uno
    const finishButtons = screen.getAllByText(/Finalizar/i)
    expect(finishButtons.length).toBeGreaterThan(0)
  })

  it('valida campo de trabajo vacío', async () => {
    setup()
    // Pulsamos el primer botón "Finalizar"
    const finishButtons = screen.getAllByText(/Finalizar/i)
    fireEvent.click(finishButtons[0])

    // Comprobamos que aparece el mensaje de validación
    const error = await screen.findByText(/campo obligatorio/i)
    expect(error).toBeDefined()
  })
})

