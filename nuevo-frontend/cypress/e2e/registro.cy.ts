/* eslint-env cypress */
// cypress/e2e/registro.cy.ts
import { userFixture } from '../__fixtures__/user.fixtures'

describe('Flujo completo de registro', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/')
    cy.url().should('include', '/register/contact')
  })

  it('Completa registro → preferencias → accede al Dashboard y primer juego', () => {
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

    // 4) Clic en el primer minijuego
    cy.get('.game-card').first().click({ force: true })

    // 5) Comprobar que se carga la escena correcta
    cy.url().should('match', /\/game\/\d+$/)
    cy.contains('h1', 'Minijuego').should('exist')
  })

  it('Bloquea acceso directo a juegos sin haber registrado datos', () => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/games/1')

    // Debe redirigir al paso 1 de registro
    cy.url().should('include', '/register/contact')
    cy.contains('h1', 'Paso 1 de 2 – Datos de contacto').should('exist')
  })
})

