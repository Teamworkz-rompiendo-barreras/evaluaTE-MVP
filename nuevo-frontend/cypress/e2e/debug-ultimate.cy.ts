/* eslint-env cypress */
// cypress/e2e/debug-ultimate.cy.ts

describe('Debug Ultimate', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/')
  })

  it('Debug completo sin asumir nada', () => {
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
    cy.contains('button', 'Finalizar y empezar minijuegos').click({ force: true })

    // 3) Verificar la URL después del clic
    cy.url().then((url) => {
      cy.log('URL después del clic:', url)
    })

    // 4) Esperar un momento para que se cargue la página
    cy.wait(2000)

    // 5) Verificar el contenido de la página sin asumir nada
    cy.get('body').then(($body) => {
      cy.log('Contenido completo de la página:', $body.text())
      
      // Verificar si hay algún h1
      const h1s = $body.find('h1')
      cy.log(`Encontrados ${h1s.length} elementos h1`)
      h1s.each((index, element) => {
        cy.log(`H1 ${index}: ${element.textContent}`)
      })
      
      // Verificar si hay algún elemento con "EvalúaTE"
      if ($body.text().includes('EvalúaTE')) {
        cy.log('✅ Encontrado "EvalúaTE" en la página')
      } else {
        cy.log('❌ NO encontrado "EvalúaTE" en la página')
      }
      
      // Verificar si hay algún elemento con "Minijuegos"
      if ($body.text().includes('Minijuegos')) {
        cy.log('✅ Encontrado "Minijuegos" en la página')
      } else {
        cy.log('❌ NO encontrado "Minijuegos" en la página')
      }
      
      // Verificar si hay algún elemento con "Debug Info"
      if ($body.text().includes('Debug Info')) {
        cy.log('✅ Encontrado "Debug Info" en la página')
      } else {
        cy.log('❌ NO encontrado "Debug Info" en la página')
      }
      
      // Verificar si hay algún error
      if ($body.text().includes('Error') || $body.text().includes('error')) {
        cy.log('⚠️ Encontrado posible error en la página')
      }
    })

    // 6) Verificar si hay algún elemento con clase que contenga "game"
    cy.get('body').then(($body) => {
      const gameElements = $body.find('[class*="game"]')
      cy.log(`Encontrados ${gameElements.length} elementos con clase que contiene "game"`)
      gameElements.each((index, element) => {
        cy.log(`Elemento ${index}: ${element.className}`)
      })
    })

    // 7) Verificar si hay algún grid
    cy.get('body').then(($body) => {
      const grids = $body.find('.grid')
      cy.log(`Encontrados ${grids.length} elementos con clase "grid"`)
    })

    // 8) Verificar si hay algún elemento con clase "game-card"
    cy.get('body').then(($body) => {
      const gameCards = $body.find('.game-card')
      cy.log(`Encontrados ${gameCards.length} elementos con clase "game-card"`)
    })
  })
}) 