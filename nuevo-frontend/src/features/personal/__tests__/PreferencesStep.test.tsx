import '@testing-library/jest-dom';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '../../../app/store';
import PreferencesStep from '../PreferencesStep';

describe('PreferencesStep', () => {
  function setup() {
    render(
      <Provider store={store}>
        <BrowserRouter>
          <PreferencesStep />
        </BrowserRouter>
      </Provider>
    );
  }

  it('muestra los campos y el botón de Finalizar', () => {
    setup();
    expect(screen.getByLabelText(/tipo de trabajo/i)).toBeInTheDocument();
    expect(screen.getByText(/Finalizar/i)).toBeInTheDocument();
  });

  it('valida campo de trabajo vacío', async () => {
    setup();
    // Pulsar Finalizar sin escribir nada
    fireEvent.click(screen.getByText('Finalizar'));
    // Aparece el mensaje de validación
    expect(await screen.findByText(/campo obligatorio/i)).toBeInTheDocument();
  });
});
