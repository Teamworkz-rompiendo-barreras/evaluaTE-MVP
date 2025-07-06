/* eslint-env cypress */
// cypress/e2e/gameflow.cy.ts
import { userFixture } from '../__fixtures__/user.fixtures'

describe('Flujo completo de usuario: registro → juegos → resultados', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/')
  })

  it('registra al usuario, completa minijuegos y genera informe final', () => {
    // ——————————————
    // 1) Registro – Paso 1: Datos personales
    // ——————————————
    cy.get('#firstName').type(userFixture.firstName, { force: true })
    cy.get('#lastName').type(userFixture.lastName, { force: true })
    cy.get('#email').type(userFixture.email, { force: true })
    cy.get('#whatsapp').type(userFixture.whatsapp, { force: true })
    cy.contains('button', 'Siguiente').click({ force: true })

    // ——————————————
    // 2) Registro – Paso 2: Preferencias laborales
    // ——————————————
    cy.url().should('include', '/preferences')
    cy.get('#jobPreferences').type(userFixture.jobPreferences.areas.join(', '), { force: true })
    cy.get('#workMode').select(userFixture.jobPreferences.workMode, { force: true })
    cy.get('#availability').select(userFixture.jobPreferences.availability, { force: true })
    if (userFixture.jobPreferences.willingToRelocate) {
      cy.get('#relocate').check({ force: true })
    }
    if (userFixture.jobPreferences.hasDisabilityCert) {
      cy.get('#cert').check({ force: true })
    }
    cy.contains('button', 'Finalizar y empezar minijuegos').click({ force: true })

    // ——————————————
    // 3) Dashboard – Acceso a los minijuegos
    // ——————————————
    cy.url().should('include', '/games')
    cy.contains('h1', 'EvalúaTE - Minijuegos').should('exist')

    // ——————————————
    // 4) Juego 1 – Primer minijuego
    // ——————————————
    cy.get('.game-card').first().click({ force: true })

    // Verificar que se carga la escena del juego
    cy.url().should('match', /\/game\/\d+$/)
    cy.contains('h1', 'Minijuego').should('exist')

    // Simular completar el juego
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

    // Volver al dashboard
    cy.visit('/games')

    // ——————————————
    // 5) Navega al informe final
    // ——————————————
    cy.contains('button', 'Ver Resultados').click({ force: true })
    cy.url().should('include', '/resultados')

    // Verifica que el informe muestre información básica
    cy.contains('h1', 'Informe de Resultados').should('exist')
  })
})