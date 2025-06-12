// cypress/e2e/gameflow.cy.ts

describe('Flujo completo de juego y desbloqueo', () => {
  it('Completa el minijuego 0 y desbloquea el 1', () => {
    // 1) Empezamos en el dashboard
    cy.visit('http://localhost:5173/games')

    // 2) El primer GameCard (id=0) es un enlace <a href="/games/0">
    cy.get('a[href^="/games/"]').first().click()

    // 3) Avanzamos por todas las escenas
    function avanzarEscena() {
      cy.get('button')
        .contains('Siguiente')
        .then(($btn) => {
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

    // 6) Ahora hay al menos dos enlaces de juego y el segundo apunta a /games/1
    cy.get('a[href^="/games/"]')
      .should('have.length.at.least', 2)
      .eq(1)
      .should('have.attr', 'href', '/games/1')
  })
})
