// Usa fetch nativo de Node.js 18+ (no necesitas instalar node-fetch)
fetch('http://localhost:8080/api/informe-ia', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    preferences: { area: "Tecnología" },
    minigames: [],
    cvAnalysis: {}
  })
})
  .then(res => res.json())
  .then(json => console.log(json))
  .catch(err => console.error(err));