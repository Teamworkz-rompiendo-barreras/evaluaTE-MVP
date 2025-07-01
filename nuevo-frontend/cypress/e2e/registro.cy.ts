// cypress/e2e/registro.cy.ts
import { mockUser } from '../__fixtures__/user.fixtures'

describe('Flujo completo de registro', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.url().should('include', '/register/contact')
  })

  it('Completa registro → preferencias → accede al Dashboard y primer juego', () => {
    // 1) Paso 1 - Datos personales
    cy.get('#firstName').type(mockUser.firstName)
    cy.get('#lastName').type(mockUser.lastName)
    cy.get('#email').type(mockUser.email)
    cy.get('#whatsapp').type(mockUser.whatsapp)

    cy.contains('button', 'Continuar').click()

    // 2) Paso 2 - Preferencias laborales
    cy.url().should('include', '/preferences')

    cy.get('#jobPreferences').type('Desarrollo web')
    cy.get('#workMode').select('remoto')
    cy.get('#availability').select('mañana')
    cy.get('#startDate').select('inmediata')
    cy.get('#relocate').check()
    cy.get('#cert').check()

    cy.contains('button', 'Guardar y continuar').click()

    // 3) Acceso al Dashboard
    cy.url().should('include', '/games')
    cy.contains('h1', 'Minijuegos completados').should('exist')

    // 4) Clic en el primer minijuego
    cy.get('.game-card').first().click()

    // 5) Comprobar que se carga la escena correcta
    cy.url().should('match', /\/games\/\d+$/)
    cy.contains('h2', 'Minijuego ').should('exist') // Puede variar según título real
  })

  it('Bloquea acceso directo a juegos sin haber registrado datos', () => {
    cy.clearLocalStorage()
    cy.visit('/games/1')

    // Debe redirigir al paso 1 de registro
    cy.url().should('include', '/register/contact')
    cy.contains('p', 'Paso 1 de 2').should('exist')
  })
})