const fs = require('fs');
const axios = require('axios');

axios.post('http://localhost:8000/api/generate-report', {
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
}, {
  responseType: 'arraybuffer'
})
  .then(response => {
    fs.writeFileSync('informe-prueba.pdf', response.data);
    console.log('PDF guardado como informe-prueba.pdf');
  })
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