/* eslint-env cypress */
// cypress/e2e/test-simple-dashboard-simple.cy.ts

describe('Test Simple Dashboard Simple', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/')
  })

  it('Verifica que el dashboard simple se carga', () => {
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
    cy.contains('h1', 'EvalúaTE - Minijuegos (SIMPLE)').should('exist')

    // 4) Verificar que hay contenido en el grid
    cy.get('.grid').should('exist')
    cy.get('.grid').children().should('have.length.at.least', 1)

    // 5) Verificar que hay al menos una tarjeta de juego
    cy.get('.game-card').should('exist')
    cy.get('.game-card').should('have.length.at.least', 1)

    // 6) Verificar que la primera tarjeta es clickeable
    cy.get('.game-card').first().should('be.visible')
    cy.get('.game-card').first().click({ force: true })

    // 7) Verificar debug info
    cy.contains('Debug Info:').should('exist')
    cy.contains('Total de juegos:').should('exist')
  })
}) 