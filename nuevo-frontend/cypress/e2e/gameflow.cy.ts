// cypress/e2e/gameflow.cy.ts

describe('Flujo completo de registro, juego y desbloqueo', () => {
  it('Registra al usuario, completa el minijuego 0 y desbloquea el 1', () => {
    // ——————————————
    // 1) Registro – Paso 1
    // ——————————————
    cy.clearLocalStorage()
    cy.visit('/register/contact')
    cy.get('#firstName').type('Ester')
    cy.get('#lastName').type('Pérez')
    cy.get('#email').type('ester@example.com')
    cy.get('button[type=submit]').click()

    // ——————————————
    // 2) Registro – Paso 2
    // ——————————————
    cy.url().should('include', '/register/preferences')
    cy.get('#jobPreferences').type('Desarrollo web')
    cy.get('#workMode').select('remoto')
    cy.get('#availability').select('mañana')
    cy.get('#startDate').select('inmediata')
    cy.get('#relocate').check()
    cy.get('#cert').check()
    cy.get('button[type=submit]').click()

    // ——————————————
    // 3) Dashboard
    // ——————————————
    cy.url().should('include', '/games')
    cy.contains('Elige un minijuego').should('exist')

    // ——————————————
    // 4) Clic en el primer juego (id=0)
    // ——————————————
    cy.get('a[href^="/games/"]').first().click()

    // ——————————————
    // 5) Avanzar por todas las escenas
    // ——————————————
    function avanzarEscena() {
      cy.get('button').contains('Siguiente').then(($btn) => {
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
    cy.get('button').contains('Finalizar').click()
    cy.url().should('include', '/games')

    // ——————————————
    // 7) Verificar que el segundo juego (id=1) está desbloqueado
    // ——————————————
    cy.get('a[href^="/games/"]')
      .should('have.length.at.least', 2)
      .eq(1)
      .should('not.have.attr', 'aria-disabled', 'true')
  })
})