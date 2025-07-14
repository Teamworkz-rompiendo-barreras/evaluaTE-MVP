/* eslint-env cypress */
// cypress/e2e/test-simple.cy.ts

describe('Test Simple - Verificación básica', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
  })

  it('Carga la página principal correctamente', () => {
    cy.visit('/')
    cy.url().should('include', '/register/contact')
    cy.contains('h1', 'Paso 1 de 2 – Datos de contacto').should('exist')
  })

  it('Puede escribir en los campos de formulario', () => {
    cy.visit('/')
    
    // Escribir en los campos
    cy.get('#firstName').type('Test', { force: true })
    cy.get('#lastName').type('User', { force: true })
    cy.get('#email').type('test@test.com', { force: true })
    cy.get('#whatsapp').type('123456789', { force: true })
    
    // Verificar que los valores se escribieron
    cy.get('#firstName').should('have.value', 'Test')
    cy.get('#lastName').should('have.value', 'User')
    cy.get('#email').should('have.value', 'test@test.com')
    cy.get('#whatsapp').should('have.value', '123456789')
  })

  it('Puede navegar a preferencias', () => {
    cy.visit('/')
    
    // Llenar formulario
    cy.get('#firstName').type('Test', { force: true })
    cy.get('#lastName').type('User', { force: true })
    cy.get('#email').type('test@test.com', { force: true })
    cy.get('#whatsapp').type('123456789', { force: true })
    
    // Hacer clic en siguiente
    cy.contains('button', 'Siguiente').click({ force: true })
    
    // Verificar que llegamos a preferencias
    cy.url().should('include', '/preferences')
    cy.contains('h2', 'Paso 2 de 2').should('exist')
  })
}) 