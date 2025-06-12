// cypress/e2e/gameflow.cy.ts

describe('Flujo completo de registro, juego y desbloqueo', () => {
  it('Registra al usuario, completa el minijuego 0 y desbloquea el 1', () => {
    // 1) Limpiamos estado y vamos a registro paso 1
    cy.clearLocalStorage()
    cy.visit('/register/contact')
    cy.get('#firstName').type('Ester')
    cy.get('#lastName').type('Pérez')
    cy.get('#email').type('ester@example.com')
    cy.get('button[type=submit]').click()

    // 2) Registro paso 2
    cy.url().should('include', '/register/preferences')
    cy.get('#jobPreferences').type('Desarrollo web')
    cy.get('#workMode').select('remoto')
    cy.get('#availability').select('mañana')
    cy.get('#startDate').select('inmediata')
    cy.get('#relocate').check()
    cy.get('#cert').check()
    cy.get('button[type=submit]').click()

    // 3) Dashboard
    cy.url().should('include', '/games')
    cy.contains('Elige un minijuego').should('be.visible')

    // 4) Abrimos el primer juego
    cy.get('a[aria-disabled="false"]').first().click()

    // 5) Recorremos todas las escenas pulsando el botón "Siguiente"
    function avanzarEscena() {
      cy.contains('button', 'Siguiente').then($btn => {
        if ($btn.is(':visible')) {
          cy.wrap($btn).click()
          avanzarEscena()
        }
      })
    }
    avanzarEscena()

    // 6) Finalizar
    cy.contains('button', 'Finalizar').click()
    cy.url().should('include', '/games')

    // 7) Comprobamos que el segundo juego (id=1) ya está habilitado
    cy.get('a[aria-disabled="false"]')
      .should('have.length.at.least', 2)
      .eq(1)
      .should('exist')
  })
})
