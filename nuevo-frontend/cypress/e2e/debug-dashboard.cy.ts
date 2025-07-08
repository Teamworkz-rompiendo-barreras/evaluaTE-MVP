/* eslint-env cypress */
// cypress/e2e/debug-dashboard.cy.ts

describe('Debug Dashboard', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/')
  })

  it('Verifica que el dashboard carga correctamente', () => {
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
    cy.contains('h1', 'EvalúaTE - Minijuegos').should('exist')

    // 4) Debug: Verificar qué elementos están presentes
    cy.get('body').then(() => {
      // Verificar si hay algún div con clase que contenga "game"
      cy.log('Buscando elementos con clase que contenga "game"')
      cy.get('[class*="game"]').then(($elements) => {
        cy.log(`Encontrados ${$elements.length} elementos con clase que contiene "game"`)
        $elements.each((index, element) => {
          cy.log(`Elemento ${index}: ${element.className}`)
        })
      })
    })

    // 5) Debug: Verificar si hay algún grid o contenedor
    cy.get('.grid').should('exist')
    cy.get('.grid').children().should('have.length.at.least', 1)

    // 6) Debug: Verificar el contenido del grid
    cy.get('.grid').children().first().then(($firstChild) => {
      cy.log('Primer elemento del grid:', $firstChild.prop('className'))
    })
  })
}) 