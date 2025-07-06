/* eslint-env cypress */
// cypress/e2e/test-test-page.cy.ts

describe('Test TestPage', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/')
  })

  it('Verifica que TestPage se carga', () => {
    // 1) Completar registro básico
    cy.get('#firstName').type('Test', { force: true })
    cy.get('#lastName').type('User', { force: true })
    cy.get('#email').type('test@test.com', { force: true })
    cy.get('#whatsapp').type('123456789', { force: true })
    cy.contains('button', 'Siguiente').click({ force: true })

    // 2) Completar preferencias básicas
    cy.get('#jobPreferences').type('Test job', { force: true })
    cy.get('#workMode').select('remoto', { force: true })
    cy.get('#availability').select('mañana', { force: true })
    cy.get('#startDate').select('inmediata', { force: true })
    cy.get('#relocate').check({ force: true })
    cy.get('#cert').check({ force: true })
    cy.contains('button', 'Finalizar y empezar minijuegos').click({ force: true })

    // 3) Verificar que llegamos al dashboard
    cy.url().should('include', '/games')
    
    // 4) Verificar que TestPage se carga
    cy.contains('h1', 'EvalúaTE - Minijuegos (TEST)').should('exist')
    cy.contains('Página de prueba para verificar que funciona').should('exist')
    cy.contains('Información de Prueba').should('exist')
  })
}) 