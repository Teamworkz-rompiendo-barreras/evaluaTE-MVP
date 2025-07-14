/* eslint-env cypress */
/// <reference types="cypress" />
// cypress/e2e/report.cy.ts
describe('Informe de Resultados', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
  })

  it('intercepta la llamada y verifica el PDF', () => {
    // Completar el flujo completo primero
    cy.visit('/')
    
    // Registro
    cy.get('#firstName').type('Test', { force: true })
    cy.get('#lastName').type('User', { force: true })
    cy.get('#email').type('test@test.com', { force: true })
    cy.get('#whatsapp').type('123456789', { force: true })
    cy.contains('button', 'Siguiente').click({ force: true })

    // Preferencias
    cy.get('#jobPreferences').type('Desarrollo web', { force: true })
    cy.get('#workMode').select('remoto', { force: true })
    cy.get('#availability').select('mañana', { force: true })
    cy.get('#startDate').select('inmediata', { force: true })
    cy.get('#relocate').check({ force: true })
    cy.get('#cert').check({ force: true })
    cy.contains('button', 'Finalizar y empezar minijuegos').click({ force: true })

    // Completar al menos un juego (simular)
    cy.url().should('include', '/games')
    
    // Simular que se completó un juego
    cy.window().then((win) => {
      win.localStorage.setItem('persist:root', JSON.stringify({
        game: JSON.stringify({
          completedGames: ['1'],
          currentGameId: null,
          gameLogs: {},
          softSkills: [],
          adaptations: []
        })
      }))
    })

    // Ir a resultados
    cy.visit('/resultados')

    // Interceptamos la petición al endpoint de generación de PDF
    cy.intercept('POST', '/api/generate-report').as('generateReport')

    // Pulsamos el botón de descarga
    cy.get('button').contains('Descargar Informe PDF').click({ force: true })

    // Comprobamos la petición y su respuesta
    cy.wait('@generateReport').then(({ response }) => {
      expect(response && response.statusCode).to.equal(200)
      expect(response && response.headers['content-type']).to.include('application/pdf')
      expect(response && response.body.length).to.be.greaterThan(1000)
    })
  })
})
