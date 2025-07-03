/// <reference types="cypress" />
// cypress/e2e/report.cy.ts
describe('Informe de Resultados', () => {
  before(() => {
    // Aquí podrías dejar preparado el estado: registro, completar un minijuego, subir CV...
    // Pero si tu app ya puede arrancar directamente en /resultados con datos mockeados,
    // simplemente visita esa ruta.
  })

  it('intercepta la llamada y verifica el PDF', () => {
    cy.visit('/resultados')

    // Interceptamos la petición al endpoint de generación de PDF
    cy.intercept('POST', '/api/generate-report').as('generateReport')

    // Pulsamos el botón de descarga
    cy.get('button').contains(/Descargar Informe/i).click()

    // Comprobamos la petición y su respuesta
    cy.wait('@generateReport').then(({ response }) => {
      expect(response!.statusCode).to.equal(200)
      expect(response!.headers['content-type']).to.include('application/pdf')
      expect(response!.body.length).to.be.greaterThan(1000)
    })
  })
})
