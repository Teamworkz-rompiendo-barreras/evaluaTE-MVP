describe('Flujo completo de juego y desbloqueo', () => {
  it('Completa el minijuego 0 y desbloquea el 1', () => {
    // 1) Empezamos en el dashboard
    cy.visit('http://localhost:5173/games')

    // 2) El primer GameCard (id=0) debe estar habilitado
    cy.get('[aria-disabled="false"]')
      .contains('🎮')
      .first()
      .click()

    // 3) Avanzamos por todas las escenas
    //    Asumimos que hay un botón con texto 'Siguiente'
    function avanzarEscena() {
      cy.get('button').contains('Siguiente').then(($btn) => {
        if ($btn.is(':visible')) {
          cy.wrap($btn).click()
          avanzarEscena()
        }
      })
    }
    avanzarEscena()

    // 4) Al final, aparece el botón Finalizar
    cy.get('button').contains('Finalizar').click()

    // 5) Volvemos al dashboard
    cy.url().should('include', '/games')

    // 6) Ahora el segundo GameCard (id=1) debe estar habilitado
    cy.get('[aria-disabled="false"]')
      .contains('🎮')
      .eq(1)
      .should('exist')
  })
})
