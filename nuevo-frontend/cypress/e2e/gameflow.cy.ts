/* eslint-env cypress */
// cypress/e2e/gameflow.cy.ts
import { userFixture } from '../__fixtures__/user.fixtures'
import { mockScene1, mockScene3 } from '../../src/features/games/__fixtures__/scene.fixture'
import { userDecision1, userDecision3 } from '../../src/features/games/__fixtures__/user.decision.fixture'

describe('Flujo completo de usuario: registro → juegos → resultados', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.visit('/')
  })

  it('registra al usuario, completa minijuegos y genera informe final', () => {
    // ——————————————
    // 1) Registro – Paso 1: Datos personales
    // ——————————————
    cy.get('#firstName').type(userFixture.firstName)
    cy.get('#lastName').type(userFixture.lastName)
    cy.get('#email').type(userFixture.email)
    cy.contains('button', 'Continuar').click()

    // ——————————————
    // 2) Registro – Paso 2: Preferencias laborales
    // ——————————————
    cy.url().should('include', '/preferences')
    cy.get('#jobPreferences').type(userFixture.jobPreferences.areas.join(', '))
    cy.get('#workMode').select(userFixture.jobPreferences.workMode)
    cy.get('#availability').select(userFixture.jobPreferences.availability)
    cy.get('#relocate').check(userFixture.jobPreferences.willingToRelocate)
    cy.get('#cert').check(userFixture.jobPreferences.hasDisabilityCert)
    cy.contains('button', 'Guardar y continuar').click()

    // ——————————————
    // 3) Dashboard – Acceso a los minijuegos
    // ——————————————
    cy.url().should('include', '/games')
    cy.contains('h1', 'Minijuegos completados').should('exist')

    // ——————————————
    // 4) Juego 0 – Toma de decisiones
    // ——————————————
    cy.get('[data-cy="game-card-0"]').click()

    cy.contains('p', mockScene1.steps[0].text).should('exist')
    cy.contains('button', userDecision1.optionText).click()
    cy.contains('button', 'Siguiente').click()

    // ——————————————
    // 5) Juego 1 – Resolución de problemas
    // ——————————————
    cy.get('[data-cy="game-card-1"]').click()

    cy.contains('p', mockScene3.steps[0].text).should('exist')
    cy.contains('button', userDecision3.optionText).click()
    cy.contains('button', 'Finalizar').click()

    // ——————————————
    // 6) Navega al informe final
    // ——————————————
    cy.contains('button', 'Ver Resultados').click()
    cy.url().should('include', '/resultados')

    // Verifica que el informe muestre puntaje global
    cy.contains('.employabilityScore', '75%').should('exist')

    // Verifica soft skills evaluadas
    cy.contains('li', 'Toma de decisiones: Alto (90% de confianza)')
    cy.contains('li', 'Resolución de problemas: Medio (65% de confianza)')

    // Descarga el informe PDF
    cy.contains('button', 'Descargar Informe PDF').click()
    cy.wait(1000) // Simula tiempo de generación
    cy.contains('div', 'Informe descargado correctamente').should('exist')
  })
})