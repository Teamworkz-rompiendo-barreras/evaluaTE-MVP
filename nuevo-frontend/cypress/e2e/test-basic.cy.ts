/* eslint-env cypress */
// cypress/e2e/test-basic.cy.ts

describe('Test Básico', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/')
  })

  it('Verifica que la aplicación se carga', () => {
    // 1) Verificar que llegamos a la página de registro
    cy.url().should('include', '/register/contact')
    
    // 2) Verificar que el formulario está presente
    cy.get('#firstName').should('exist')
    cy.get('#lastName').should('exist')
    cy.get('#email').should('exist')
    cy.get('#whatsapp').should('exist')
    
    // 3) Completar registro básico
    cy.get('#firstName').type('Test', { force: true })
    cy.get('#lastName').type('User', { force: true })
    cy.get('#email').type('test@test.com', { force: true })
    cy.get('#whatsapp').type('123456789', { force: true })
    cy.contains('button', 'Siguiente').click({ force: true })

    // 4) Verificar que llegamos a preferencias
    cy.url().should('include', '/preferences')
    cy.get('#jobPreferences').should('exist')
    
    // 5) Completar preferencias básicas
    cy.get('#jobPreferences').type('Test job', { force: true })
    cy.get('#workMode').select('remoto', { force: true })
    cy.get('#availability').select('mañana', { force: true })
    cy.get('#startDate').select('inmediata', { force: true })
    cy.get('#relocate').check({ force: true })
    cy.get('#cert').check({ force: true })
    cy.contains('button', 'Finalizar y empezar minijuegos').click({ force: true })

    // 6) Verificar que llegamos al dashboard
    cy.url().should('include', '/games')
    
    // 7) Verificar que hay algún contenido en la página
    cy.get('body').should('contain', 'EvalúaTE')
    
    // 8) Debug: Ver qué hay en la página
    cy.get('body').then(($body) => {
      cy.log('Contenido de la página:', $body.text())
    })
  })
}) 