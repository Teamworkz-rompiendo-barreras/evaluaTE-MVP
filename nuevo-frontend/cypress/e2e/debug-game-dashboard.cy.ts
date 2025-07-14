/* eslint-env cypress */
// cypress/e2e/debug-game-dashboard.cy.ts

describe('Debug GameDashboardPage', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/')
  })

  it('Debug específico del GameDashboardPage', () => {
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
    
    // 4) Debug: Verificar si el título del dashboard está presente
    cy.contains('h1', 'EvalúaTE - Minijuegos').should('exist')
    
    // 5) Debug: Verificar si hay algún grid
    cy.get('.grid').should('exist')
    
    // 6) Debug: Verificar cuántos elementos hay en el grid
    cy.get('.grid').children().then(($children) => {
      cy.log(`Grid tiene ${$children.length} elementos`)
    })
    
    // 7) Debug: Verificar si hay algún elemento con clase que contenga "game"
    cy.get('[class*="game"]').then(($elements) => {
      cy.log(`Encontrados ${$elements.length} elementos con clase que contiene "game"`)
      $elements.each((index, element) => {
        cy.log(`Elemento ${index}: ${element.className}`)
      })
    })
    
    // 8) Debug: Verificar si hay algún elemento con la clase exacta "game-card"
    cy.get('.game-card').then(($elements) => {
      cy.log(`Encontrados ${$elements.length} elementos con clase "game-card"`)
    })
    
    // 9) Debug: Verificar el contenido completo de la página
    cy.get('body').then(($body) => {
      cy.log('Contenido completo de la página:', $body.text())
    })
    
    // 10) Debug: Verificar si hay algún error en la consola
    cy.window().then((win) => {
      cy.log('Console logs:', win.console.log)
    })
  })
}) 