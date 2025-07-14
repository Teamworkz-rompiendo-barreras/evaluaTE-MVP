// Usa fetch nativo de Node.js 18+ (no necesitas instalar node-fetch)
fetch('http://localhost:8080/api/informe-ia', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    gameData: [
      { subject: 'Minijuego 1', dA: 80 },
      { subject: 'Minijuego 2', dA: 90 }
    ],
    cvAnalysis: {
      structure: 'bueno',
      coherence: 'bueno',
      experience: 'media',
      skills: ['habilidad1', 'habilidad2']
    },
    jobPreferences: {
      areas: ['Tecnología', 'Educación'],
      needs: ['Trabajo remoto'],
      workMode: 'remoto'
    }
  })
})
  .then(res => res.json())
  .then(json => console.log(json))
  .catch(error => {
    if (error.response && error.response.data) {
      // Intenta decodificar el buffer como texto
      const errorText = Buffer.from(error.response.data).toString('utf8');
      try {
        const errorJson = JSON.parse(errorText);
        console.error('Error generando el PDF:', errorJson);
      } catch {
        console.error('Error generando el PDF:', errorText);
      }
    } else {
      console.error('Error generando el PDF:', error.message);
    }
  });