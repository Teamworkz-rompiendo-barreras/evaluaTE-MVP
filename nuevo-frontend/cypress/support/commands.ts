/* eslint-env cypress */
// cypress/support/commands.ts

// Importar el plugin de subida de archivos
import 'cypress-file-upload'

// Comando para limpiar localStorage y manejar modals
Cypress.Commands.add('clearStorageAndHandleModals', () => {
  cy.clearLocalStorage()
  cy.clearCookies()
  
  // Esperar un momento para que se carguen los modales
  cy.wait(1000)
  
  // Manejar cualquier modal que pueda aparecer
  cy.get('body').then(($body) => {
    // Verificar si hay modales de privacidad
    if ($body.find('[role="dialog"]').length > 0) {
      // Intentar manejar modal de privacidad
      if ($body.find('#privacy-consent').length > 0) {
        cy.get('#privacy-consent').check({ force: true })
        cy.contains('button', 'Aceptar y continuar').click({ force: true })
      }
      // Intentar manejar modal de cookies
      else if ($body.find('#cookie-consent-title').length > 0) {
        cy.contains('button', 'Aceptar todas').click({ force: true })
      }
      
      // Esperar a que el modal desaparezca
      cy.get('[role="dialog"]').should('not.exist', { timeout: 10000 })
    }
  })
  
  // Manejar específicamente el modal de cookies que puede aparecer
  cy.get('body').then(($body) => {
    if ($body.find('.fixed.bottom-0.left-0.right-0').length > 0) {
      cy.contains('button', 'Aceptar todas').click({ force: true })
      cy.get('.fixed.bottom-0.left-0.right-0').should('not.exist', { timeout: 10000 })
    }
  })
  
  // Esperar un momento adicional para asegurar que todo esté listo
  cy.wait(500)
})

Cypress.Commands.add('login', () => {
  cy.visit('/register/contact')
  cy.get('#firstName').should('be.visible').type('Usuario', { force: true })
  cy.get('#lastName').should('be.visible').type('Prueba', { force: true })
  cy.get('#email').should('be.visible').type('usuario@ejemplo.com', { force: true })
  cy.get('#whatsapp').should('be.visible').type('987654321', { force: true })
  cy.contains('button', 'Siguiente').click({ force: true })
})

Cypress.Commands.add('completePreferences', () => {
  cy.get('#jobPreferences').should('be.visible').type('Desarrollo web', { force: true })
  cy.get('#workMode').should('be.visible').select('remoto')
  cy.get('#availability').should('be.visible').select('mañana')
  cy.get('#startDate').should('be.visible').select('inmediata')
  cy.get('#relocate').should('be.visible').check({ force: true })
  cy.get('#cert').should('be.visible').check({ force: true })
  cy.contains('button', 'Finalizar y empezar minijuegos').click({ force: true })
})