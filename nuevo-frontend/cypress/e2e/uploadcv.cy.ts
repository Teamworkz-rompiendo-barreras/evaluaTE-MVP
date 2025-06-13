describe('Flujo de subida de CV', () => {
  it('Permite subir un PDF y redirige a resultados', () => {
    cy.clearLocalStorage();
    cy.visit('/register/contact');
    // (aquí repetimos registro rápido…)
    cy.get('#firstName').type('Ana');
    cy.get('#lastName').type('García');
    cy.get('button[type=submit]').click();
    cy.get('#jobPreferences').type('Soporte');
    cy.get('button[type=submit]').click();
    cy.visit('/subircv');
    cy.get('input[type="file"]').attachFile('example.pdf'); // necesitas un fixture example.pdf
    cy.get('button').contains('Analizar CV').click();
    cy.url().should('include', '/resultados');
    cy.contains('Tu puntuación de CV').should('exist');
  });
});
