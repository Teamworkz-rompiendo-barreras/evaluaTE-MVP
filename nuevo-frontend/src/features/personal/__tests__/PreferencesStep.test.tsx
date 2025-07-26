/* eslint-env jest */
/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import PreferencesStep from '../PreferencesStep'

// Store de prueba simple
const testStore = configureStore({
  reducer: {
    personal: (state = {}, _action) => state,
    progress: (state = {}, _action) => state,
    accessibility: (state = {}, _action) => state,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

describe('PreferencesStep', () => {
  function setup() {
    render(
      <Provider store={testStore}>
        <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <PreferencesStep />
        </BrowserRouter>
      </Provider>
    )
  }

  it('muestra los campos y el botón de continuar', () => {
    setup()
    // Buscamos el input por su label y comprobamos que existe
    const jobInput = screen.getByLabelText(/tipo de trabajo/i)
    expect(jobInput).toBeDefined()

    // Buscamos el botón "Continuar a los minijuegos" y comprobamos que existe
    const continueButton = screen.getByText(/Continuar a los minijuegos/i)
    expect(continueButton).toBeDefined()
  })

  it('valida campo de trabajo vacío', async () => {
    setup()
    // Pulsamos el botón "Continuar a los minijuegos"
    const continueButton = screen.getByText(/Continuar a los minijuegos/i)
    fireEvent.click(continueButton)

    // Comprobamos que aparece el mensaje de validación
    const error = await screen.findByText(/campo obligatorio/i)
    expect(error).toBeDefined()
  })
})

