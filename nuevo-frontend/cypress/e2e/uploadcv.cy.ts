/* eslint-env cypress */
describe('Flujo de subida de CV', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
  })

  it('Permite subir un PDF y redirige a resultados', () => {
    cy.visit('/')
    
    // Registro rápido
    cy.get('#firstName').type('Ana', { force: true })
    cy.get('#lastName').type('García', { force: true })
    cy.get('#email').type('ana@ejemplo.com', { force: true })
    cy.get('#whatsapp').type('123456789', { force: true })
    cy.contains('button', 'Siguiente').click({ force: true })
    
    // Preferencias
    cy.get('#jobPreferences').type('Soporte', { force: true })
    cy.get('#workMode').select('remoto', { force: true })
    cy.get('#availability').select('completa', { force: true })
    cy.get('#startDate').select('inmediata', { force: true })
    cy.get('#relocate').check({ force: true })
    cy.get('#cert').check({ force: true })
    cy.contains('button', 'Finalizar y empezar minijuegos').click({ force: true })
    
    // Simular que se completaron todos los juegos
    cy.url().should('include', '/games')
    cy.window().then((win) => {
      win.localStorage.setItem('persist:root', JSON.stringify({
        game: JSON.stringify({
          completedGames: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
          currentGameId: null,
          gameLogs: {},
          softSkills: [],
          adaptations: []
        })
      }))
    })
    
    // Navegar a subida de CV
    cy.visit('/upload-cv')
    
    // Subir archivo (necesitamos crear un archivo de prueba)
    cy.fixture('example.pdf').then(fileContent => {
      cy.get('input[type="file"]').attachFile({
        fileContent: fileContent,
        fileName: 'example.pdf',
        mimeType: 'application/pdf'
      })
    })
    
    cy.get('button').contains('Analizar CV').click({ force: true })
    cy.url().should('include', '/resultados')
    cy.contains('Informe de Resultados').should('exist')
  })
})
