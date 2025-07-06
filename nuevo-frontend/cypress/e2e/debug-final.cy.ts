/* eslint-env cypress */
// cypress/e2e/debug-final.cy.ts

describe('Debug Final', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/')
  })

  it('Debug completo del flujo', () => {
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
    
    // 3) Debug: Verificar que el botón está presente antes de hacer clic
    cy.contains('button', 'Finalizar y empezar minijuegos').should('exist')
    cy.contains('button', 'Finalizar y empezar minijuegos').should('be.visible')
    
    // 4) Hacer clic en el botón
    cy.contains('button', 'Finalizar y empezar minijuegos').click({ force: true })

    // 5) Debug: Verificar la URL después del clic
    cy.url().then((url) => {
      cy.log('URL después del clic:', url)
    })

    // 6) Debug: Verificar si hay algún error en la consola
    cy.window().then((win) => {
      cy.log('Console logs:', win.console.log)
    })

    // 7) Debug: Verificar el contenido de la página
    cy.get('body').then(($body) => {
      cy.log('Contenido completo de la página:', $body.text())
    })

    // 8) Debug: Verificar si hay algún elemento con "EvalúaTE"
    cy.get('body').then(($body) => {
      if ($body.text().includes('EvalúaTE')) {
        cy.log('✅ Encontrado "EvalúaTE" en la página')
      } else {
        cy.log('❌ NO encontrado "EvalúaTE" en la página')
      }
    })

    // 9) Debug: Verificar si hay algún h1
    cy.get('h1').then(($h1s) => {
      cy.log(`Encontrados ${$h1s.length} elementos h1`)
      $h1s.each((index, element) => {
        cy.log(`H1 ${index}: ${element.textContent}`)
      })
    })

    // 10) Debug: Verificar si hay algún error visible
    cy.get('body').then(($body) => {
      if ($body.text().includes('Error') || $body.text().includes('error')) {
        cy.log('⚠️ Encontrado posible error en la página')
      }
    })
  })
}) 