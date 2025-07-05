/* eslint-env cypress */
// cypress/support/commands.ts
Cypress.Commands.add('login', () => {
  cy.visit('/register/contact')
  cy.get('#firstName').type('Usuario')
  cy.get('#lastName').type('Prueba')
  cy.get('#email').type('usuario@ejemplo.com')
  cy.get('#whatsapp').type('987654321')
  cy.contains('button', 'Continuar').click()
})

Cypress.Commands.add('completePreferences', () => {
  cy.get('#jobPreferences').type('Desarrollo web')
  cy.get('#workMode').select('remoto')
  cy.get('#availability').select('mañana')
  cy.get('#startDate').select('inmediata')
  cy.get('#relocate').check()
  cy.get('#cert').check()
  cy.contains('button', 'Guardar y continuar').click()
})