/* eslint-env cypress */
// cypress/e2e/test-original-debug.cy.ts
import { userFixture } from '../__fixtures__/user.fixtures'

describe('Test Original Debug', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/')
    cy.url().should('include', '/register/contact')
  })

  it('Replica exactamente el test original con debug', () => {
    // 1) Paso 1 - Datos personales
    cy.get('#firstName').type(userFixture.firstName, { force: true })
    cy.get('#lastName').type(userFixture.lastName, { force: true })
    cy.get('#email').type(userFixture.email, { force: true })
    cy.get('#whatsapp').type(userFixture.whatsapp, { force: true })

    cy.contains('button', 'Siguiente').click({ force: true })

    // 2) Paso 2 - Preferencias laborales
    cy.url().should('include', '/preferences')

    cy.get('#jobPreferences').type('Desarrollo web', { force: true })
    cy.get('#workMode').select('remoto', { force: true })
    cy.get('#availability').select('mañana', { force: true })
    cy.get('#startDate').select('inmediata', { force: true })
    cy.get('#relocate').check({ force: true })
    cy.get('#cert').check({ force: true })

    cy.contains('button', 'Finalizar y empezar minijuegos').click({ force: true })

    // 3) Acceso al Dashboard
    cy.url().should('include', '/games')
    cy.contains('h1', 'EvalúaTE - Minijuegos').should('exist')

    // Debug: Verificar que las tarjetas están presentes
    cy.get('.game-card').should('have.length.at.least', 1)
    cy.get('.game-card').should('be.visible')

    // Debug: Verificar el contenido de la página
    cy.get('body').then(($body) => {
      cy.log('Contenido de la página en test original debug:', $body.text())
    })

    // 4) Clic en el primer minijuego
    cy.get('.game-card').first().click({ force: true })

    // 5) Comprobar que se carga la escena correcta
    cy.url().should('match', /\/game\/\d+$/)
    cy.contains('h1', 'Minijuego').should('exist')
  })
}) 