import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',
    specPattern: 'cypress/e2e/**/*.cy.ts',
    supportFile: false,    // si no usas support
  },
})

describe('Flujo completo de registro, juego y desbloqueo', () => {
  
  beforeEach(() => {
    // Limpiamos cualquier estado anterior
    cy.clearLocalStorage();
    cy.visit(`register/contact`);
  });

  it('Registra al usuario, completa el minijuego 0 y desbloquea el 1', () => {
    // ——————————————
    // 1) Registro – Paso 1
    // ——————————————
    cy.get('#firstName').type('Ester');
    cy.get('#lastName').type('Pérez');
    cy.get('#email').type('ester@example.com');
    cy.get('button[type=submit]').click();

    // ——————————————
    // 2) Registro – Paso 2
    // ——————————————
    cy.url().should('include', '/register/preferences');
    cy.get('#jobPreferences').type('Desarrollo web');
    cy.get('#workMode').select('remoto');
    cy.get('#availability').select('mañana');
    cy.get('#startDate').select('inmediata');
    cy.get('#relocate').check();
    cy.get('#cert').check();
    cy.get('button[type=submit]').click();

    // ——————————————
    // 3) Dashboard
    // ——————————————
    cy.url().should('include', '/games');
    cy.contains('Elige un minijuego').should('be.visible');

    // ——————————————
    // 4) Abrimos el primer juego (id=0)
    // ——————————————
    cy.get('[data-cy="game-card-0"]')
      .should('have.attr', 'aria-disabled', 'false')
      .click();

    // ——————————————
    // 5) Recorremos todas las escenas
    // ——————————————
   function avanzarEscena() {
      cy.contains('button', 'Siguiente').then($btn => {
        if ($btn.is(':visible')) {
          cy.wrap($btn).click()
          avanzarEscena()
        }
      })
    }
    avanzarEscena()

    // ——————————————
    // 6) Finalizar y volver al dashboard
    // ——————————————
    cy.contains('button', 'Finalizar').click();
    cy.url().should('include', '/games');

    // ——————————————
    // 7) El segundo juego (id=1) ya está habilitado
    // ——————————————
    cy.get('[data-cy="game-card-1"]')
      .should('have.attr', 'aria-disabled', 'false');
  });
});
