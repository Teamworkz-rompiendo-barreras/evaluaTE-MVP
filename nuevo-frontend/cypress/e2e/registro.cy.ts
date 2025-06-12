// cypress/e2e/registro.cy.ts

describe('Flujo de registro y acceso al juego', () => {
  it('Completa registro y puede acceder al Dashboard y a un juego', () => {
    // 1) Registro – Paso 1
    cy.visit('/register/contact')
    cy.get('#firstName').type('Ester')
    cy.get('#lastName').type('Pérez')
    cy.get('#email').type('ester@example.com')
    cy.get('button[type=submit]').click()

    // 2) Registro – Paso 2
    cy.url().should('include', '/register/preferences')
    cy.get('#jobPreferences').type('Desarrollo web')
    cy.get('#workMode').select('remoto')
    cy.get('#availability').select('mañana')
    cy.get('#startDate').select('inmediata')
    cy.get('#relocate').check()
    cy.get('#cert').check()
    cy.get('button[type=submit]').click()

    // 3) Dashboard
    cy.url().should('include', '/games')
    cy.contains('Elige un minijuego').should('exist')

    // 4) Clic en el primer juego
    cy.get('a[href^="/games/"]').first().click()

    // 5) Comprobar que carga la página de juego (solo URL, sin depender del contenido)
    cy.url().should('match', /\/games\/\d+$/)
  })

  it('Bloquea el acceso directo a un juego sin registro', () => {
    // Limpiar cualquier estado previo
    cy.clearLocalStorage()

    // Intentar entrar directamente
    cy.visit('/register/contact')

    // Debe redirigir al inicio del registro
    cy.location('pathname').should('include', '/register/contact')
    cy.contains('Paso 1 de 2').should('exist')
  })
})
