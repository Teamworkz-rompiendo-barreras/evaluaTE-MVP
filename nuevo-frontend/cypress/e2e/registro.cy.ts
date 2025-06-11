describe('Flujo registro y dashboard', () => {
  it('Completa registro y entra al Dashboard', () => {
    cy.visit('http://localhost:5173/register/contact')
    // Paso 1: Datos Personales
    cy.get('#firstName').type('Ester')
    cy.get('#lastName').type('Pérez')
    cy.get('#email').type('ester@example.com')
    cy.get('button[type=submit]').click()

    // Paso 2: Preferencias
    cy.url().should('include', '/register/preferences')
    cy.get('#jobPreferences').type('Desarrollo web')
    cy.get('#workMode').select('remoto')
    cy.get('#availability').select('mañana')
    cy.get('#startDate').select('inmediata')
    cy.get('#relocate').check()
    cy.get('#cert').check()
    cy.get('button[type=submit]').click()

    // Llega al Dashboard de juegos
    cy.url().should('include', '/games')
    cy.contains('Tus juegos').should('exist')
  })
})
